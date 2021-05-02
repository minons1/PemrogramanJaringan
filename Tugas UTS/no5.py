import socket
from bs4 import BeautifulSoup

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('classroom.its.ac.id', 80)
client_socket.connect(server_address)

request_header = b'GET / HTTP/1.0\r\nHost: classroom.its.ac.id\r\n\r\n'
client_socket.send(request_header)

response = ''
while True:
    received = client_socket.recv(1024)
    if not received:
        break
    response += received.decode('utf-8')

responses = response.rsplit('\r\n',1)
body = responses[1]

soup = BeautifulSoup(body, 'html.parser')
print(soup.title.string)


# title = responses[1].split('\n')
# print(title)

# print(response)
client_socket.close()
