import socket
import threading
import json
import sqlite3
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5555
DB_NAME = "nexatalk.db"
clients = {}
lock = threading.Lock()


def init_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at TEXT NOT NULL
            )
        """)


def save_message(username, message, sent_at):
    with sqlite3.connect(DB_NAME) as db:
        db.execute(
            "INSERT INTO messages (username, message, sent_at) VALUES (?, ?, ?)",
            (username, message, sent_at)
        )


def get_history(limit=100):
    with sqlite3.connect(DB_NAME) as db:
        rows = db.execute(
            "SELECT username, message, sent_at FROM messages ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    rows.reverse()
    return [
        {"type": "message", "username": row[0], "text": row[1], "time": row[2]}
        for row in rows
    ]


def clear_history():
    with sqlite3.connect(DB_NAME) as db:
        db.execute("DELETE FROM messages")


def send_packet(sock, packet):
    payload = json.dumps(packet, ensure_ascii=False) + "\n"
    sock.sendall(payload.encode("utf-8"))


def broadcast(packet):
    with lock:
        recipients = list(clients.keys())

    failed = []
    for sock in recipients:
        try:
            send_packet(sock, packet)
        except OSError:
            failed.append(sock)

    for sock in failed:
        remove_client(sock)


def broadcast_users():
    with lock:
        names = sorted(clients.values(), key=str.lower)
    broadcast({"type": "users", "users": names})


def remove_client(sock):
    with lock:
        username = clients.pop(sock, None)

    try:
        sock.close()
    except OSError:
        pass

    if username:
        print(f"{username} disconnected.")
        broadcast({"type": "system", "text": f"{username} left the room."})
        broadcast_users()


def handle_client(sock, address):
    username = None
    reader = None

    try:
        reader = sock.makefile("r", encoding="utf-8")
        first_line = reader.readline()
        if not first_line:
            return

        login = json.loads(first_line)
        username = str(login.get("username", "")).strip()

        if not username or len(username) > 20 or "\n" in username:
            send_packet(sock, {"type": "error", "text": "Use a username between 1 and 20 characters."})
            return

        with lock:
            if any(name.casefold() == username.casefold() for name in clients.values()):
                send_packet(sock, {"type": "error", "text": "That username is already online. Choose another one."})
                return
            clients[sock] = username

        send_packet(sock, {"type": "history", "messages": get_history()})
        broadcast({"type": "system", "text": f"{username} joined NexaTalk."})
        broadcast_users()
        print(f"{username} connected from {address}")

        for line in reader:
            try:
                packet = json.loads(line)
            except json.JSONDecodeError:
                continue

            if packet.get("type") == "clear_history":
                # Shared room history is cleared for everyone.
                clear_history()
                broadcast({"type": "clear_history"})
                broadcast({"type": "system", "text": f"{username} cleared the conversation."})
                continue

            if packet.get("type") != "message":
                continue

            message = str(packet.get("text", "")).strip()
            if not message or len(message) > 1500:
                continue

            sent_at = datetime.now().strftime("%I:%M %p")
            save_message(username, message, sent_at)
            broadcast({
                "type": "message",
                "username": username,
                "text": message,
                "time": sent_at
            })

    except (OSError, ValueError, json.JSONDecodeError):
        pass
    finally:
        remove_client(sock)


def main():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen()
        print("=" * 48)
        print("             NEXATALK SERVER")
        print("=" * 48)
        print(f"Listening on {HOST}:{PORT}")
        print("Database: nexatalk.db")
        print("Waiting for members...\n")

        while True:
            sock, address = server.accept()
            threading.Thread(
                target=handle_client,
                args=(sock, address),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        print("\nNexaTalk server stopped.")
    finally:
        with lock:
            active = list(clients.keys())
        for sock in active:
            remove_client(sock)
        server.close()


if __name__ == "__main__":
    main()