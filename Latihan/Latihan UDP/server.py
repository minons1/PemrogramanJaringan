import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 5000))
while True:
    data,address = s.recvfrom(25)
    print(data, address)

