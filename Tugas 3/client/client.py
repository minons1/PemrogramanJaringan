import socket
import sys

class Client:
    def __init__(self):
        # self.host = '192.168.100.219'
        self.host = '192.168.43.225'
        self.port = 5000
        self.client = None
        self.size = 1024

    def open_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))

    def run(self):
        self.open_socket()
        try:
            while True:
                pesan = input()
                self.client.send(pesan.encode('utf-8'))
       
        except KeyboardInterrupt:
            self.client.close()
            sys.exit(0)

if __name__ == "__main__" :
    client = Client()
    client.run()
