import socket
import pickle
import sys
import threading
import time

from messageclass import Message

class Client:
    def __init__(self):
        # self.host = '192.168.100.219'
        self.host = '127.0.0.1'
        self.port = 5000
        self.client = None
        self.size = 65536
        self.thread = threading.Thread(target=self.recv_msg)
        self.game_mode = 0

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
            res = b''
            while True:
                packet = self.client.recv(self.size)
                res += packet

                if len(packet) < self.size - 1:
                    break


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
                    if (res.message == "file transfer"):
                        self.save_file(res.filename,res.attachment)

                    # elif(res.message == "game_on"):
                    #     # enter to game function
                    #     self.game_mode = 1

                    elif(res.message == "bye 0/"):
                        break

    def get_file(self, filename):
        try: 
            f = open('../dataset/'+filename, 'rb')
            data = f.read()
            f.close()

        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            print ('file error')
            return -1
            
        filedata = pickle.dumps(data)

        return filedata
    
    def save_file(self, filename, filedata):
        f =  open('./assets/'+filename,'wb')
        f.write(pickle.loads(filedata))
        f.close()
        print ("File " + filename + " has been saved")

    def run(self):
        self.open_socket()
        try:
            print("Welcome to DimSal Messager!\ntype !help if you need help, !exit if you done\ninput your username first :", end="")
            username = input()
            self.client.send(username.encode('utf-8'))
            while True:
                # if self.game_mode == 1:
                #     # self.gameRoom()
                #     pass
                
                # else :
                pesan = input()
                pesan = pesan.split(" ",3)
                if(pesan[0] == "!exit"):
                    self.send_msg("server",pesan,None,None)
                    raise KeyboardInterrupt

                elif(pesan[0] == "!help"):
                    self.send_msg("server",pesan,None,None)
                
                elif(pesan[0] == "!addfriend"):
                    self.send_msg("server",pesan,None,None)
                
                elif(pesan[0] == "!friendlist"):
                    self.send_msg("server",pesan,None,None)
                    
                elif(pesan[0] == "!listroom"):
                    self.send_msg("server",pesan,None,None)

                elif(pesan[0] == "!createroom"):
                    self.send_msg("server",pesan,None,None)

                elif(pesan[0] == "!enterroom"):
                    self.send_msg("server",pesan,None,None)
                    # wait to enter the room
                    time.sleep(3)

                elif(pesan[0] == "!send"):
                    if(pesan[1] == "-b"):
                        self.send_msg("broadcast",pesan,None,None)

                    elif(pesan[1] == "-f"):
                        self.send_msg("pesan[2]",pesan,None,None)

                    elif(pesan[1] == "-a"):
                        self.send_msg("friends",pesan,None,None)

                    elif(pesan[1] == "-c"):
                        self.send_msg("room",pesan,None,None)
                
                    elif(pesan[1] == "-ft"):
                        if len(pesan) > 3:
                            filename = pesan[3]
                            filedata = self.get_file(filename)
                            if(filedata != -1):
                                self.send_msg("friends",pesan,filename,filedata)
                                print("File " + filename + " has been sent to server")
                            else:
                                continue
                        else:
                            print("Please input filename")
                else:
                    self.send_msg("server",pesan,None,None)
                
        except KeyboardInterrupt:
            self.close_socket()

if __name__ == "__main__" :
    client = Client()
    client.run()
