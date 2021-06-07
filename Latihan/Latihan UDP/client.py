import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("127.0.0.1", 5000))
s.send(b"Hello")
s.send(b" World")
s.close()

