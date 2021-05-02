import select
import socket
import sys
import threading
from configparser import ConfigParser
from os import listdir
from os.path import isfile, join
from urllib.parse import unquote


class Server:
    def __init__(self,port):
        self.host = '192.168.43.225'
        self.port = port
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
    def run(self):
        self.open_socket()
        input_list = [self.server, sys.stdin]
        running = 1
        while running:
            input_ready, _, _ = select.select(input_list, [], [])

            for s in input_ready:

                if s == self.server:
                    # handle the server socket
                    client_socket, client_address = self.server.accept()
                    c = Client(client_socket, client_address)
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    _ = sys.stdin.readline()
                    running = 0

        # close all threads

        self.server.close()
        for c in self.threads:
            c.join()


class Client(threading.Thread):
    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.dataset = ['/'+f for f in listdir('./dataset/') if isfile(join('./dataset/', f))]
    
    def get_index(self,response_headers, response_data) :
        f = open('index.html', 'r')
        response_data = f.read()
        f.close()
        
        content_length = len(response_data)
        response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                            + str(content_length) + '\r\n\r\n'

        self.client.sendall(response_header.encode('utf-8') + response_data.encode('utf-8'))

    def get_file(self, file, response_headers, response_data):
        f = open('./dataset'+file, 'rb')
        response_data = f.read()
        f.close()
        
        content_length = len(response_data)
        response_header = 'HTTP/1.1 200 OK\r\nContent-Length:' \
                            + str(content_length) + '\r\n\r\n'

        self.client.sendall(response_header.encode('utf-8') + response_data)

    def get_404(self,response_headers, response_data):
        f = open('404.html', 'r')
        response_data = f.read()
        f.close()
        
        content_length = len(response_data)
        response_header = 'HTTP/1.1 404 Not found\r\nContent-Length:' \
                            + str(content_length) + '\r\n\r\n'

        self.client.sendall(response_header.encode('utf-8') + response_data.encode('utf-8'))

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            if data:
                print("masuk")
                data = data.decode('utf-8')
                print(data)
                
                request_header = data.split('\r\n')
                request_file = request_header[0].split()[1]
                request_file = unquote(request_file)
                print(request_file)

                response_header = b''
                response_data = b''
                
                if request_file == 'index.html' or request_file == '/' or request_file == '/index.html':
                    self.get_index(response_header, response_data)

                elif request_file in self.dataset:
                    self.get_file(request_file,response_header, response_data)
                
                else:
                    self.get_404(response_header, response_data)
            else:
                self.client.close()
                running = 0


if __name__ == "__main__":
    parser = ConfigParser()
    parser.read('httpserver.conf')
    PORT = int(parser.get('PORT', 'port3'))

    server = Server(PORT)
    server.run()
