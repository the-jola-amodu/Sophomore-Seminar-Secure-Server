# Real-Time Secure Chat & Cybersecurity Showcase

This project was developed for a **Sophomore Seminar** to demonstrate both the mechanics of real-time web communication using **Flask-SocketIO** and the critical importance of **server-side security**.

The repository contains two versions of the same application:

- **`Web server - INSECURE/`**: A *naive* implementation vulnerable to several common web attacks.  
- **`Web server - SECURE/`**: A hardened version implementing robust sanitization, rate limiting, and resource management.

---

## 🚀 Features

- **Real-time Messaging**: Instant communication using WebSockets.  
- **Room-based Chat**: Unique room codes for private sessions.  
- **File Sharing**: Secure file uploads with automatic timestamping and sanitized path handling.  
- **Active Member Tracking**: Real-time updates of who is currently in the room.  
- **Mobile-Responsive Design**: Styled with Tailwind CSS for a modern, responsive UI.

---

## 🧪 The Vulnerability Showcase

The primary goal of this project is to demonstrate how common vulnerabilities can be exploited in a live environment. Below are the five main exploits showcased during the seminar:

| Vulnerability        | Exploitation Method                                                                 | Mitigation (The Fix)                                                                 |
|----------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Stored XSS**        | Injecting `<script>alert('XSS')</script>` into the chat.                              | Server-side escaping using `markupsafe.escape`.                                      |
| **Username Spoofing** | Registering as `ADMIN<div style="...">` to fake authority.                            | Sanitizing usernames before storing them in the session.                             |
| **Message DoS**      | A JS loop in the console sending 5,000+ messages.                                     | Enforcing a `MAX_HISTORY_MESSAGES` limit on the server.                               |
| **Rate Limit Bypass**| Bypassing client-side delays by calling `emit()` directly.                           | Server-side timestamp tracking (e.g., max 5 messages per 5 seconds).                 |                        |
