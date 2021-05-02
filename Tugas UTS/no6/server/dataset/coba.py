import socket
from bs4 import BeautifulSoup

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.43.225', 12345)
client_socket.connect(server_address)

request_header = b'GET /aa.jpg HTTP/1.0\r\nHost: 192.168.43.225:12345\r\n\r\n'
client_socket.send(request_header)

response = b''
while True:
    received = client_socket.recv(1024)
    response += received
    if len(received) < 1024:
        break


responses = response.split(b'\r\n',3)
content = responses[3]
with open('aa.jpg', 'wb') as file:
    file.write(content)


client_socket.close()
