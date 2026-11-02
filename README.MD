✦ NexaTalk – Real-Time Community Chat Application
A modern desktop chat application built with Python, CustomTkinter, TCP sockets, multithreading, JSON messaging, and SQLite.
Features
Multi-user username login
Real-time messaging
Live online members list
SQLite-backed chat history
Clear shared conversation from the app
Message timestamps
Premium dark desktop interface
Duplicate username protection
Requirements
Python 3.10+
Windows, macOS, or Linux desktop
Installation
pip install -r requirements.txt
Run the application
Open a terminal in the project folder and start the server:
python server.py
Keep the server running. Open another terminal for each user:
python client.py
Use a different username in each client window.
Important notes
The default host is 127.0.0.1, so this setup is for testing on one computer.
Messages are stored in nexatalk.db using SQLite and remain after server restarts.
The Clear conversation button clears the shared message history for all connected clients.
Do not share private or sensitive information in a demo chat.
Project Information
Project: NexaTalk
Track: Python Programming
Internship Organization: Oasis Infobyte
Developer: Aditi Khobragade
Technologies
Python · CustomTkinter · Socket Programming · TCP/IP · Threading · JSON · SQLite