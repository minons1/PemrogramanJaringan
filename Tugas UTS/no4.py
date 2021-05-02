import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('monta.if.its.ac.id', 80)
client_socket.connect(server_address)

request_header = b'GET / HTTP/1.0\r\nHost: monta.if.its.ac.id\r\n\r\n'
client_socket.send(request_header)

response = ''
while True:
    received = client_socket.recv(1024)
    if not received:
        break
    response += received.decode('utf-8')

headers = response.split('\r\n')
print(headers[7])

# print(response)
client_socket.close()
