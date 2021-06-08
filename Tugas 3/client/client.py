import socket
import pickle
import sys
import threading

from messageclass import Message

class Client:
    def __init__(self):
        # self.host = '192.168.100.219'
        self.host = '192.168.43.225'
        self.port = 5000
        self.client = None
        self.size = 65535
        self.thread = threading.Thread(target=self.recv_msg)

    def open_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        self.thread.start()
    
    def close_socket(self):
        self.thread.join()
        self.client.close()
        sys.exit(0)

    # Function for send msg to server 
    def send_msg(self,receiver,message,filename,attachment):
        req = Message(self.client.getsockname(),receiver,message,filename,attachment)
        req = pickle.dumps(req)
        self.client.send(req)

    # Thread function for handle recv msg from server
    def recv_msg(self):
        while True:
            res = self.client.recv(self.size)
            if(len(res)==0):
                break
            else:
                # TO-DO handle recv msg with file attachment
                res = pickle.loads(res)
                if(type(res.message) == dict):
                    print("[{}] : list command available".format(res.sender))
                    for k,v in res.message.items():
                        print(k," : ",v)
                else:
                    print("[{}] : {}".format(res.sender,res.message))
                    if(res.message == "bye 0/"):
                        break
    
    

    def run(self):
        self.open_socket()
        try:
            print("Welcome to DimSal Messager!\ntype !help if you need help, !exit if you done\ninput your username first :", end="")
            username = input()
            self.client.send(username.encode('utf-8'))
            while True:
                pesan = input()
                pesan = pesan.split(" ",3)
                if(pesan[0] == "!exit"):
                    self.send_msg("server",pesan,None,None)
                    raise KeyboardInterrupt

                elif(pesan[0] == "!help"):
                    self.send_msg("server",pesan,None,None)

                elif(pesan[0] == "!send"):
                    if(pesan[1] == "-b"):
                        self.send_msg("broadcast",pesan,None,None)

                    elif(pesan[1] == "-f"):
                        self.send_msg(pesan[2],pesan,None,None)

                    elif(pesan[1] == "-a"):
                        # to-do add friend
                        pass

                    elif(pesan[1] == "-ft"):
                        #to-do file transfer
                        pass

                else:
                    self.send_msg("server",pesan,None,None)
                
       
        except KeyboardInterrupt:
            self.close_socket()

if __name__ == "__main__" :
    client = Client()
    client.run()
