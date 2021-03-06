import os
import socket
import select
import sys
from configparser import ConfigParser

def get_index(sock, response_headers, response_data) :
    f = open('index.html', 'r')
    response_data = f.read()
    f.close()
    
    content_length = len(response_data)
    response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                        + str(content_length) + '\r\n\r\n'

    sock.sendall(response_header.encode('utf-8') + response_data.encode('utf-8'))


thisfolder = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(thisfolder, 'httpserver.conf')

parser = ConfigParser()
parser.read(filepath)
PORT = int(parser.get('PORT', 'port3'))

server_address = ('127.0.0.1', PORT)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

try:
    while True:
        read_ready, write_ready, exception = select.select(input_socket, [], [])
        
        for sock in read_ready:
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                input_socket.append(client_socket)                       
            
            else:            
                print ("masuk")
                # receive data from client, break when null received          
                data = sock.recv(1024)
                print(data)
                
                data = data.decode('utf-8')
                request_header = data.split('\r\n')
                request_file = request_header[0].split()[1]
                response_header = b''
                response_data = b''
                print(request_file)
                if request_file == 'index.html' or request_file == '/' or request_file == '/index.html':
                    get_index(sock, response_header, response_data)

                else:
                    sock.sendall(b'HTTP/1.1 404 Not found\r\n\r\n')

                # sock.close()
                # input_socket.remove(sock)

except KeyboardInterrupt:        
    server_socket.close()
    sys.exit(0)
