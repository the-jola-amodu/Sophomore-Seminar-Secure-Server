import socket

HEADER = 64
PORT = 50501
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    server_response_length_header = client.recv(HEADER).decode(FORMAT)
    
    if server_response_length_header:
        server_response_length = int(server_response_length_header)
        server_response = client.recv(server_response_length).decode(FORMAT)
        
        print(f"[SERVER]: {server_response}")
    else:
        print("[ERROR] Failed to receive header from server.")

send("Hello World")