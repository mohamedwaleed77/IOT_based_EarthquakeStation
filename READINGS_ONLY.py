import socket

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005     # Listening port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


counter=0
def receive_message():
    global counter
    data, addr = sock.recvfrom(1024)  # Receive message
    print(f"Received from {addr[0]}:{addr[1]} -> {data.decode()}")
    counter+=1
    print (counter)
    return data.decode(), addr

     
while True:
    msg, sender = receive_message()  # Receive a message
 
