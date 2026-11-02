import socket
import threading
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5555

BG = "#10121B"
SIDEBAR = "#171A27"
PANEL = "#1B1F2E"
CARD = "#252A3B"
ACCENT = "#8B70FF"
ACCENT_HOVER = "#7459E8"
TEXT = "#F5F4FA"
MUTED = "#9BA2B8"
GREEN = "#35D49A"
RED = "#FF647C"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NexaTalk(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NexaTalk | Real-Time Community")
        self.geometry("1180x760")
        self.minsize(900, 600)
        self.sock = None
        self.connected = False
        self.closing = False
        self.username = ""
        self.messages = []
        self.show_login()
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def show_login(self):
        self.login = ctk.CTkFrame(
            self, fg_color=SIDEBAR, corner_radius=24,
            border_width=1, border_color="#34394D"
        )
        self.login.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.login, text="✦", font=("Arial", 48, "bold"),
            text_color=ACCENT
        ).pack(pady=(32, 0))

        ctk.CTkLabel(
            self.login, text="NexaTalk", font=("Arial", 35, "bold"),
            text_color=TEXT
        ).pack(padx=65, pady=(0, 4))

        ctk.CTkLabel(
            self.login, text="REAL-TIME CHAT. REAL CONNECTION.",
            font=("Arial", 10, "bold"), text_color=MUTED
        ).pack(pady=(0, 25))

        self.name_entry = ctk.CTkEntry(
            self.login, width=330, height=48,
            placeholder_text="Choose your display name",
            corner_radius=12, font=("Arial", 14)
        )
        self.name_entry.pack(padx=35, pady=8)
        self.name_entry.bind("<Return>", lambda event: self.connect())

        ctk.CTkButton(
            self.login, text="Enter NexaTalk  →",
            width=330, height=48, corner_radius=12,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("Arial", 14, "bold"), command=self.connect
        ).pack(padx=35, pady=(14, 32))

    def connect(self):
        name = self.name_entry.get().strip()
        if not name or len(name) > 20 or "\n" in name:
            messagebox.showwarning("Display name", "Enter a name between 1 and 20 characters.")
            return

        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_sock.connect((HOST, PORT))
            new_sock.sendall((json.dumps({"username": name}) + "\n").encode("utf-8"))
            self.sock = new_sock
            self.username = name
            self.connected = True
            self.closing = False
            self.build_app()
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except OSError as error:
            new_sock.close()
            messagebox.showerror(
                "Connection failed",
                "Please start server.py first.\n\n" + str(error)
            )

    def build_app(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="✦  NexaTalk",
            font=("Arial", 23, "bold"), text_color=TEXT
        ).pack(anchor="w", padx=18, pady=(27, 34))

        self.side_label("YOUR SPACE")
        self.side_item("⌂   Community")
        self.side_item("#   general", active=True)
        self.side_item("#   introductions")
        self.side_item("#   random")

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#34394D").pack(
            fill="x", padx=16, pady=22
        )
        self.side_label("YOUR PROFILE")

        ctk.CTkLabel(
            self.sidebar, text=f"●  {self.username}",
            text_color=GREEN, font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=19, pady=8)

        ctk.CTkLabel(
            self.sidebar, text="Connected to NexaTalk",
            text_color=MUTED, font=("Arial", 10)
        ).pack(anchor="w", padx=19)

        ctk.CTkLabel(
            self.sidebar, text="PYTHON • SOCKET CHAT",
            text_color=MUTED, font=("Arial", 9, "bold")
        ).pack(side="bottom", pady=22)

        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=14, height=76)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_propagate(False)

        titlebox = ctk.CTkFrame(header, fg_color="transparent")
        titlebox.pack(side="left", padx=18, pady=12)
        ctk.CTkLabel(
            titlebox, text="#  general", font=("Arial", 19, "bold"), text_color=TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            titlebox, text="A friendly place to connect and collaborate",
            font=("Arial", 10), text_color=MUTED
        ).pack(anchor="w")

        self.connection_label = ctk.CTkLabel(
            header, text="● CONNECTING", text_color=GREEN,
            font=("Arial", 10, "bold")
        )
        self.connection_label.pack(side="right", padx=18)

        self.chat = ctk.CTkScrollableFrame(
            self.main, fg_color=PANEL, corner_radius=14
        )
        self.chat.grid(row=1, column=0, sticky="nsew")
        self.chat.grid_columnconfigure(0, weight=1)

        self.welcome = ctk.CTkFrame(self.chat, fg_color="transparent")
        self.welcome.pack(fill="x", pady=(45, 25))
        ctk.CTkLabel(
            self.welcome, text="✦", font=("Arial", 35), text_color=ACCENT
        ).pack()
        ctk.CTkLabel(
            self.welcome, text="Welcome to NexaTalk",
            font=("Arial", 22, "bold"), text_color=TEXT
        ).pack(pady=5)
        ctk.CTkLabel(
            self.welcome, text="This is the beginning of your conversation.",
            font=("Arial", 11), text_color=MUTED
        ).pack()

        composer = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=14)
        composer.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        composer.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkEntry(
            composer, height=46, corner_radius=11,
            placeholder_text="Message #general",
            font=("Arial", 13)
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(12, 7), pady=11)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        ctk.CTkButton(
            composer, text="Send  ➤", width=105, height=46,
            corner_radius=11, fg_color=ACCENT,
            hover_color=ACCENT_HOVER, command=self.send_message
        ).grid(row=0, column=1, padx=(4, 12), pady=11)

        self.member_panel = ctk.CTkFrame(
            self, width=205, fg_color=SIDEBAR, corner_radius=0
        )
        self.member_panel.grid(row=0, column=2, sticky="nsew")
        self.member_panel.grid_propagate(False)

        ctk.CTkLabel(
            self.member_panel, text="MEMBERS",
            font=("Arial", 14, "bold"), text_color=TEXT
        ).pack(anchor="w", padx=17, pady=(30, 20))

        ctk.CTkLabel(
            self.member_panel, text="ONLINE",
            font=("Arial", 10, "bold"), text_color=MUTED
        ).pack(anchor="w", padx=17, pady=(0, 10))

        self.users_frame = ctk.CTkScrollableFrame(
            self.member_panel, fg_color="transparent", height=400
        )
        self.users_frame.pack(fill="x", padx=8)

        self.user_count = ctk.CTkLabel(
            self.member_panel, text="0 members online",
            font=("Arial", 10), text_color=MUTED
        )
        self.user_count.pack(anchor="w", padx=17, pady=14)

        ctk.CTkButton(
            self.member_panel, text="Clear conversation",
            height=35, fg_color="#382633", hover_color="#563143",
            text_color="#FFB4C0", font=("Arial", 10, "bold"),
            command=self.clear_conversation
        ).pack(side="bottom", fill="x", padx=12, pady=18)

    def side_label(self, text):
        ctk.CTkLabel(
            self.sidebar, text=text, font=("Arial", 10, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=19, pady=(7, 9))

    def side_item(self, text, active=False):
        ctk.CTkLabel(
            self.sidebar, text=text, height=34, anchor="w",
            corner_radius=8,
            fg_color="#383052" if active else "transparent",
            text_color=TEXT if active else MUTED,
            font=("Arial", 12)
        ).pack(fill="x", padx=11, pady=2)

    def receive_loop(self):
        try:
            reader = self.sock.makefile("r", encoding="utf-8")
            for line in reader:
                if not self.connected:
                    break
                try:
                    packet = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self.after(0, self.handle_packet, packet)
        except (OSError, ValueError):
            pass
        finally:
            self.connected = False
            if not self.closing:
                try:
                    self.after(0, self.connection_lost)
                except RuntimeError:
                    pass

    def handle_packet(self, packet):
        if self.closing:
            return

        kind = packet.get("type")

        if kind == "error":
            messagebox.showerror("Could not join", packet.get("text", "Login failed."))
            self.close_app()
        elif kind == "history":
            for item in packet.get("messages", []):
                self.add_message(item.get("username", "User"), item.get("text", ""), item.get("time", ""))
        elif kind == "message":
            self.add_message(
                packet.get("username", "User"),
                packet.get("text", ""),
                packet.get("time", "")
            )
        elif kind == "system":
            self.add_system(packet.get("text", ""))
        elif kind == "users":
            self.update_users(packet.get("users", []))
        elif kind == "clear_history":
            self.messages.clear()
            for widget in self.chat.winfo_children():
                widget.destroy()
            self.add_system("Conversation cleared.")

    def add_message(self, username, text, time):
        self.messages.append({"username": username, "text": text, "time": time})
        if hasattr(self, "welcome") and self.welcome.winfo_exists():
            self.welcome.destroy()

        mine = username == self.username
        row = ctk.CTkFrame(self.chat, fg_color="transparent")
        row.pack(fill="x", padx=13, pady=6)

        bubble = ctk.CTkFrame(
            row, fg_color="#44396F" if mine else CARD,
            corner_radius=13, border_width=1,
            border_color="#5A4A91" if mine else "#353B4E"
        )
        bubble.pack(anchor="e" if mine else "w", padx=5)

        ctk.CTkLabel(
            bubble, text=f"{username}  ·  {time}",
            font=("Arial", 10, "bold"),
            text_color="#D2C8FF" if mine else GREEN
        ).pack(anchor="w", padx=13, pady=(9, 3))

        ctk.CTkLabel(
            bubble, text=text, font=("Arial", 13),
            text_color=TEXT, wraplength=420, justify="left"
        ).pack(anchor="w", padx=13, pady=(2, 10))

        self.scroll_bottom()

    def add_system(self, text):
        ctk.CTkLabel(
            self.chat, text=f"— {text} —",
            font=("Arial", 10), text_color=MUTED
        ).pack(pady=7)
        self.scroll_bottom()

    def update_users(self, users):
        for widget in self.users_frame.winfo_children():
            widget.destroy()

        for name in users:
            line = ctk.CTkFrame(self.users_frame, fg_color="transparent")
            line.pack(fill="x", pady=5)
            ctk.CTkLabel(
                line, text="●", text_color=GREEN,
                font=("Arial", 13)
            ).pack(side="left", padx=(5, 8))
            ctk.CTkLabel(
                line, text=name, text_color=TEXT,
                font=("Arial", 12)
            ).pack(side="left")

        self.user_count.configure(text=f"{len(users)} members online")
        self.connection_label.configure(text="● CONNECTED", text_color=GREEN)

    def send_message(self):
        text = self.message_entry.get().strip()
        if not text or not self.connected:
            return
        try:
            packet = {"type": "message", "text": text}
            self.sock.sendall((json.dumps(packet, ensure_ascii=False) + "\n").encode("utf-8"))
            self.message_entry.delete(0, "end")
        except OSError:
            self.connection_lost()

    def clear_conversation(self):
        if not self.connected:
            return
        confirm = messagebox.askyesno(
            "Clear conversation",
            "Clear the shared chat history for everyone? This cannot be undone."
        )
        if confirm:
            try:
                self.sock.sendall(
                    (json.dumps({"type": "clear_history"}) + "\n").encode("utf-8")
                )
            except OSError:
                self.connection_lost()

    def scroll_bottom(self):
        def scroll():
            try:
                self.chat._parent_canvas.yview_moveto(1.0)
            except (AttributeError, RuntimeError):
                pass
        self.after(100, scroll)

    def connection_lost(self):
        if hasattr(self, "connection_label"):
            self.connection_label.configure(
                text="● DISCONNECTED", text_color=RED
            )
        if hasattr(self, "chat"):
            self.add_system("Connection to server was lost.")

    def close_app(self):
        self.closing = True
        self.connected = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
        self.destroy()


if __name__ == "__main__":
    app = NexaTalk()
    app.mainloop()