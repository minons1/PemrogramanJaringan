import sys
import select
import socket
import threading
import pickle
from configparser import ConfigParser

from messageclass import Message,COMMAND_AVAILABLE
class Profile:
    def __init__(self, sock, uname):
        self.username = uname
        self.socket = sock
        self.friend = {}

    def addFriend(self, sock, uname):
        self.friend[sock] = uname

class Server:
    def __init__(self,port):
        # self.host = '192.168.100.219'
        # self.host = '192.168.43.225'
        self.host = '127.0.0.1'
        self.port = port
        self.size = 65569
        self.server = None
        self.threads = []
        self.clients = {}
        self.profiles = {}

    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    # Function to send message to client
    # receiver is a tuple (receiver_socket, receiver_username)
    def send_msg(self, sender,receiver,message,filename,attachment):
        res = Message(sender,receiver[1],message,filename,attachment)
        res = pickle.dumps(res)
        receiver[0].send(res)
    
    # Thread function thread for handle client send & recv 
    def run_client(self,client_socket,client_address):

        # Get new client's username and add to clients{}
        username = client_socket.recv(self.size)
        username = username.decode('utf-8')
        self.clients[client_socket] = username

        print(">> ",client_address, username,  "joined the server!")

        # Tuple for save this client socket and username
        this_client = (client_socket,username)

        # Add this client to profile list
        self.profiles[username] = Profile(client_socket, username)

        while True:

            req = client_socket.recv(self.size)

            if req:
                req = pickle.loads(req)

                # Check if received message command is available to handle 
                if(req.message[0] in COMMAND_AVAILABLE):

                    # Handle if client disconnect from server
                    if(req.message[0] == "!exit"):
                        print(">> ",client_address, username, "left the server!")
                        self.send_msg("server",this_client,"bye 0/",None,None)
                        self.clients.pop(client_socket)
                        break
                    
                    elif(req.message[0] == "!help"):
                        self.send_msg("server",this_client,COMMAND_AVAILABLE,None,None)

                    elif(req.message[0] == "!friendlist"):
                        friendlist = []
                        for client_sock,client_uname in self.profiles[username].friend.items():
                            friendlist.append(client_uname)
                        
                        if len(friendlist) != 0:
                            self.send_msg("server",this_client,friendlist,None,None)
                        
                        else :
                            self.send_msg("server",this_client,"You have no friends in your friendlist",None,None)

                    elif(req.message[0] == "!addfriend"):
                        name = req.message[1]
                        value = 0
                        # Check if friend's name that user want to add is exist
                        for uname, user in self.profiles.items():
                            if uname == name:
                                self.profiles[username].addFriend(user.socket, user.username)
                                self.send_msg("server",this_client, name + " is successfully added as your friend",None,None)

                                self.profiles[user.username].addFriend(this_client, username)
                                # self.send_msg("server",user.socket, username + " is successfully added you as his friend",None,None)
                                value = 1
                                break
                        
                        if value == 0 :
                            print("There is no profile with username : " + name)
                    
                    elif(req.message[0] == "!send"):
                        if(req.message[1] == "-b"):
                            for client_sock,client_uname in self.clients.items():
                                pesan = req.message[2]
                                if(len(req.message)==4):
                                    pesan += " "+req.message[3]
                                self.send_msg("BROADCAST/"+username,(client_sock,client_uname),pesan,None,None)

                        elif(req.message[1] == "-f"):
                            # TO-DO check if user is friend with sender
                            # check if user exist 
                            keys = [k for k, v in self.clients.items() if v == req.message[2]]
                            if(len(keys) == 0):
                                self.send_msg("server",this_client,"username not found",None,None)
                            else:
                                self.send_msg(this_client[1],(keys[0],req.message[2]),req.message[3],None,None)
                        
                        elif(req.message[1] == "-a"):

                            for client_sock,client_uname in self.profiles[username].friend.items():
                                pesan = req.message[2]
                                if(len(req.message)==4):
                                    pesan += " "+req.message[3]
                                self.send_msg("FRIENDS/"+username,(client_sock,client_uname),pesan,None,None)

                        elif(req.message[1] == "-ft"):
                            value = 0
                            for client_sock,client_uname in self.profiles[username].friend.items():
                                if(client_uname == req.message[2]):
                                    pesan = "file transfer"
                                    filename = req.message[3]
                                    data = req.attachment
                                    # print(req.attachment)
                                    self.send_msg("FRIENDS/"+username,(client_sock,client_uname),pesan,filename,data)
                                    value = 1
                            
                            if value == 0:
                                self.send_msg("server",this_client,req.message[2] + " is not exist in your friendlist",None,None)

                else:
                    print(req.message)
                    self.send_msg("server",this_client,"command not available",None,None)
                    
            else:
                break
        
    def run(self):
        self.open_socket()
        input_list = [self.server,sys.stdin]
        running = 1
        while running:
            # Detecting client opened 
            input_ready, _, _ = select.select(input_list, [], [])

            for s in input_ready:
                if s == self.server:
                    # Accept and Start thread to handle recv & send msg 
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



