import socket
import threading

HEADER = 64
PORT = 50501
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

msg_thread = []

print(f"Socket bound to address: {SERVER} at port {PORT}")

def send_message(connection, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    # Pad the length string to the fixed HEADER size
    send_length += b' ' * (HEADER - len(send_length))
    
    # Send the padded length (header) and then the actual message
    connection.send(send_length)
    connection.send(message)

def handle_client(connection, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = connection.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}]: {msg}")
            server_response = "Message recieved! Remember to be respectful!"
            send_message(connection, server_response)
    connection.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start():
    server.listen()
    while True:
        connection, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting... ")
start()