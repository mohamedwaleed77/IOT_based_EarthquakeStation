import socket

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005     # Listening port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def receive_message():
    data, addr = sock.recvfrom(1024)  # Receive message
    print(f"Received from {addr[0]}:{addr[1]} -> {data.decode()}")
    return data.decode(), addr

def send_message(message, target_ip, target_port):
    sock.sendto(message.encode(), (target_ip, target_port))
    print(f"Sent to {target_ip}:{target_port} -> {message}")

# Example usage:
while True:
    msg, sender = receive_message()  # Receive a message
 
