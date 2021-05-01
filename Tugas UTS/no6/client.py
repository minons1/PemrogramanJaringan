import socket
import sys

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 12345)
client_socket.connect(server_address)

request_header = b'GET / HTTP/1.0\r\n\r\n'
client_socket.send(request_header)

try :
    while True:
        message = sys.stdin.readline()
        client_socket.send(bytes(message, 'utf-8'))
        response = ''
        received = client_socket.recv(1024)
        response += received.decode('utf-8')

        print(response)
        client_socket.close()

except KeyboardInterrupt:        
    client_socket.close()
    sys.exit(0)

