import sys
import select
import socket
import threading
from configparser import ConfigParser

class Server:
    def __init__(self,port):
        # self.host = '192.168.100.219'
        self.host = '192.168.43.225'
        self.port = port
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
        input_list = [self.server,sys.stdin]
        running = 1
        while running:
            input_ready, _, _ = select.select(input_list, [], [])

            for s in input_ready:
                print(s)
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

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            if data:
                data = data.decode('utf-8')
                print(data)
            else:
                self.client.close()
                running = 0


if __name__ == "__main__":
    parser = ConfigParser()
    parser.read('httpserver.conf')
    PORT = int(parser.get('PORT', 'port3'))

    server = Server(PORT)
    server.run()
