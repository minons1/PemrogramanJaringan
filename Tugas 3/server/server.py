import sys
import select
import socket
import threading
import pickle
from configparser import ConfigParser

from messageclass import Message,COMMAND_AVAILABLE

class Server:
    def __init__(self,port):
        # self.host = '192.168.100.219'
        self.host = '192.168.43.225'
        self.port = port
        self.size = 65535
        self.server = None
        self.threads = []
        self.clients = {}

    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    # receiver is a tuple (receiver_socket, receiver_username)
    def send_msg(self, sender,receiver,message,filename,attachment):
        res = Message(sender,receiver[1],message,filename,attachment)
        res = pickle.dumps(res)
        receiver[0].send(res)
        
    def run_client(self,client_socket,client_address):
        # Get new client's username and add to clients{}
        username = client_socket.recv(self.size)
        username = username.decode('utf-8')
        self.clients[client_socket] = username

        print(">> ",client_address, username,  "joined the server!")

        # Tuple for save this client socket and username
        this_client = (client_socket,username)

        while True:
            req = client_socket.recv(self.size)
            if req:
                req = pickle.loads(req)
                if(req.message[0] in COMMAND_AVAILABLE):
                    if(req.message[0] == "!exit"):
                        print(">> ",client_address, username, "left the server!")
                        self.send_msg("server",this_client,"bye 0/",None,None)
                        self.clients.pop(client_socket)
                        break
                    elif(req.message[0] == "!help"):
                        self.send_msg("server",this_client,COMMAND_AVAILABLE,None,None)
                    elif(req.message[0] == "!send"):
                        if(req.message[1] == "-b"):
                            for client_sock,client_uname in self.clients.items():
                                pesan = req.message[2]
                                if(len(req.message)==4):
                                    pesan += " "+req.message[3]
                                self.send_msg("BROADCAST/"+username,(client_sock,client_uname),pesan,None,None)
                        elif(req.message[1] == "-f"):
                            keys = [k for k, v in self.clients.items() if v == req.message[2]]
                            if(len(keys) == 0):
                                self.send_msg("server",this_client,"username not found",None,None)
                            else:
                                self.send_msg(this_client[1],(keys[0],req.message[2]),req.message[3],None,None)
                        elif(req.message[1] == "-a"):
                            # to-do handle add friend
                            pass
                        elif(req.message[1] == "-fp"):
                            # to-do handle transfer file
                            pass
                else:
                    self.send_msg("server",this_client,"command not available",None,None)
                    
            else:
                break
        
    def run(self):
        self.open_socket()
        input_list = [self.server,sys.stdin]
        running = 1
        while running:
            input_ready, _, _ = select.select(input_list, [], [])

            for s in input_ready:
                if s == self.server:
                    # handle the server socket
                    client_socket, client_address = self.server.accept()
                    c = threading.Thread(target=self.run_client,args=(client_socket,client_address))
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

if __name__ == "__main__":
    parser = ConfigParser()
    parser.read('httpserver.conf')
    PORT = int(parser.get('PORT', 'port3'))

    server = Server(PORT)
    server.run()

# class Client(threading.Thread):
#     def __init__(self, client, address):
#         threading.Thread.__init__(self)
#         self.client = client
#         self.address = address
#         self.size = 65535

#     def run(self):
#         running = 1
#         while running:
#             request = self.client.recv(self.size)
#             if request:
#                 request = pickle.loads(request)
#                 if(request.message  in COMMAND_AVAILABLE):
#                     if(request.message == "!exit"):
#                         self.client.close()
#                         running = 0
#                     elif(request.message == "!help"):
#                         response = Message("Server",request.receiver,COMMAND_AVAILABLE)
#                         response = pickle.dumps(response)
#                         self.client
#                     elif(request.message == "!send"):
#                         pass
                    
#                     # print(data)
#             else:
#                 self.client.close()
#                 running = 0



