import sys
import select
import socket
import threading
import pickle
import random
import time
from configparser import ConfigParser

from messageclass import Message,COMMAND_AVAILABLE

class Room:
    def __init__(self):
        self.player = {}

    def addPlayer(self, sock, uname):
        if (len(self.player) < 2):
            self.player[uname] = sock
            return True
        else: 
            print("Room is full")
            return False
    
    def removePlayer(self,sock):
        del self.player[sock]

    def countPlayer(self):
        return len(self.player)

    def getPlayer(self):
        return self.player


class Profile:
    def __init__(self, sock, uname):
        self.username = uname
        self.socket = sock
        self.friend = {}
        self.room = -1

    def addFriend(self, sock, uname):
        self.friend[sock] = uname

class Server:
    def __init__(self,port):
        # self.host = '192.168.100.219'
        # self.host = '192.168.43.225'
        self.host = '127.0.0.1'
        self.port = port
        self.size = 65536
        self.server = None
        self.threads = []
        self.clients = {}
        self.profiles = {}
        self.rooms = []

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

    # delete user's friendlist (all)
    def delAllFriend(self, username, this_client):
        temp = dict(self.profiles[username].friend)
        for friend_sock,friend_uname in temp.items():
            del self.profiles[friend_uname].friend[this_client]

            del self.profiles[username].friend[friend_sock]
            self.send_msg("server",(friend_sock,friend_uname), username + " has left from the server. This user has been deleted from your friendlist",None,None)

        print(username + "'s friendlist has been deleted")

    def createRoom(self):
        self.rooms.append(Room())

    def listRoom(self):
        room = {}
        i = 0
        while i < len(self.rooms):
            room[i] = list(self.rooms[i].getPlayer().values())
            i+=1
        return room
    
    def checkRoom(self, index):
        player1_status = 0
        player2_status = 0

        def recv_msg(socket):
            req = b''
            received = socket.recv(self.size)
            req += received
            if req:
                req = pickle.loads(req)
    
            print(req.message)
            print("masuk checking room")

            return req.message[0]

        if self.rooms[index].countPlayer() == 2:
            # define players
            players = dict(self.rooms[index].getPlayer())
            players_name = list(players.values())
            players_socket = list(players.keys())

            # define player 1
            player1 = (players_socket[0],players_name[0])

            # define player 2
            player2 = (players_socket[1],players_name[1])

            # ask ready
            self.send_msg("server",player1,"Input 'ready' to play or 'leave' to leave the room",None,None)

            # recv ready
            while True:
                msg1 = recv_msg(players_socket[0])

                if msg1 == "ready":
                    player1_status = 1
                    break

                elif msg1 == "leave":
                    self.rooms[index].removePlayer(players_socket[0])
                    self.profiles[players_name[0]].room = -1
                    self.send_msg("server",player1,"You left the room",None,None)
                    self.send_msg("server",player2,"Other player left the room",None,None)
                    break

                else:
                    self.send_msg("server",player1,"Room : Wrong input!",None,None)

            self.send_msg("server",player2,"Input 'ready' to play or 'leave' to leave the room",None,None)
            while True:
                msg2 = recv_msg(players_socket[1])

                if msg2 == "ready":
                    player2_status = 1
                    break

                elif msg2 == "leave":
                    self.rooms[index].removePlayer(players_socket[1])
                    self.profiles[players_name[1]].room = -1
                    self.send_msg("server",player2,"You left the room",None,None)
                    self.send_msg("server",player1,"Other player left the room",None,None)
                    break

                else:
                    self.send_msg("server",player2,"Room : Wrong input!",None,None)

            if player1_status == 1 and player2_status == 1:
                self.send_msg("server",player2,"game_on",None,None)
                self.gameRoom(index)

            else:
                return 0
        
        else:
            return 0
        


    def gameRoom(self, index):
        i=0

        # define players
        players = dict(self.rooms[index].getPlayer())
        players_name = list(players.values())
        players_socket = list(players.keys())

        # define player 1
        player1_name = players_name[0]
        player1_socket = players_socket[0]
        player1 = (player1_socket,player1_name)
        player1_score = [0]

        #define player 2
        player2_name = players_name[1]
        player2_socket = players_socket[1]
        player2 = (player2_socket,player2_name)
        player2_score = [0]

        print(player1_name)
        print(player1_socket)
        print(player2_name)
        print(player2_socket)

        # define card 
        card = random.choices([1,2,3,4,5,6,7,8,9,10,11,12,13], k=8)
        self.send_msg("server",player1,"Time to play! This is the deck card : \n" + str(card),None,None)
        self.send_msg("server",player2,card,None,None)
        print(card)

        def recv_msg_game(socket):
            req = b''
            received = socket.recv(self.size)
            req += received
            if req:
                req = pickle.loads(req)
    
            print(req.message)
            print("recv from gameRoom")

            return req.message
        
        def player1_turn():
            while True :
                time.sleep(1)
                self.send_msg("server",player1,"Your turn",None,None)
                self.send_msg("server",player2,"Player1 turn",None,None)
                message = recv_msg_game(player1_socket)

                if message[0] == "left":
                    print("masuk left")
                    player1_score[0] += card.pop(0)
                    print(card)
                    return 1

                elif message[0] == "right":
                    player1_score[0] += card.pop(len(card)-1)
                    print(card)
                    return 1 
                
                elif message[0] == "leave":
                    return -1
                
                elif message[0] == "!send":
                    print("masuk kirim pesan")
                    if message[1] == "-c" and len(message) > 2:
                        self.send_msg("server",player2,message[2],None,None)
                    else:
                        self.send_msg("server",player1,"Room : Wrong send input!",None,None)

                else:
                    self.send_msg("server",player1,"Game : Wrong input",None,None)
                    continue

        def player2_turn():
            while True :
                time.sleep(1)
                self.send_msg("server",player2,"Your turn",None,None)
                self.send_msg("server",player1,"Player2 turn",None,None)
                message = recv_msg_game(player2_socket)

                if message[0] == "left":
                    player2_score[0] += card.pop(0)
                    print(card)
                    return 1

                elif message[0] == "right":
                    player2_score[0] += card.pop(len(card)-1)
                    print(card)
                    return 1 
                
                elif message[0] == "leave":
                    return -1
                
                elif message[0] == "!send":
                    print("masuk kirim pesan")
                    if message[1] == "-c" and len(message) > 2:
                        self.send_msg("server",player1,message[2],None,None)
                    else:
                        self.send_msg("server",player2,"Room : Wrong send input!",None,None)

                else:
                    self.send_msg("server",player2,"Game : Wrong input",None,None)
                    continue

        # recv message
        game_mode = 1
        while game_mode == 1:
            while len(card) > 0:
                # player1 turn
                turn1 = player1_turn()
                print ("turn1 = " + str(turn1))
                if turn1 == 1:
                    self.send_msg("server",player1,str(card) + "\nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score) + "\n",None,None)
                    self.send_msg("server",player2,str(card) + "\nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score) + "\n",None,None)
                elif turn1 == -1:
                    print ("Game finished, player1 is leaving the game")
                    game_mode = 0
                    self.send_msg("server",player1,"You lose!",None,None)
                    self.send_msg("server",player2,"You win! Player1 is leaving the game",None,None)
                    break
                
                # check if the match is over
                if len(card) == 1:
                    print ("Room " + str(index) + " : Game finished")
                    if (player1_score[0] > player2_score[0]):
                        self.send_msg("server",player1,"You win! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        self.send_msg("server",player2,"You lose! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        break
                    elif (player1_score[0] < player2_score[0]):
                        self.send_msg("server",player1,"You lose! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        self.send_msg("server",player2,"You win! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        break
                    else:
                        self.send_msg("server",player1,"Draw! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        self.send_msg("server",player2,"Draw! \nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score),None,None)
                        break

                # player2 turn
                turn2 = player2_turn()
                print ("turn2 = " + str(turn2))
                if turn2 == 1:
                    self.send_msg("server",player1,str(card) + "\nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score) + "\n",None,None)
                    self.send_msg("server",player2,str(card) + "\nPlayer 1's score = " + str(player1_score) + "\nPlayer 2's score = " + str(player2_score) + "\n",None,None)
                elif turn2 == -1:
                    print ("Game finished, player2 is leaving the game")
                    game_mode = 0
                    self.send_msg("server",player2,"You lose!",None,None)
                    self.send_msg("server",player1,"You win! Player2 is leaving the game",None,None)
                    break
            
            # removing player from the room
            time.sleep(1)
            self.send_msg("server",player1,"You are leaving the room",None,None)
            self.send_msg("server",player2,"You are leaving the room",None,None)
            self.rooms[index].removePlayer(player1_socket)
            self.profiles[player1_name].room = -1
            self.rooms[index].removePlayer(player2_socket)
            self.profiles[player2_name].room = -1

            print ("Game finished")
            game_mode = 0
            break
        
        return -1


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
        
        # create room
        self.createRoom()

        while True:
            print("recv from main")
            req = b''
            while True:
                received = client_socket.recv(self.size)
                req += received
                
                if len(received) < self.size - 1:
                    break

            if req:
                req = pickle.loads(req)

                # Check if received message command is available to handle 
                if(req.message[0] in COMMAND_AVAILABLE):
                    # Handle if client disconnect from server
                    if(req.message[0] == "!exit"):
                        self.delAllFriend(username, client_socket)
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
                        if len(req.message) > 1:
                            name = req.message[1]
                            value = 0
                            # Check if friend's name that user want to add is exist
                            for uname, user in self.profiles.items():
                                if uname == name:
                                    self.profiles[username].addFriend(user.socket, user.username)
                                    self.send_msg("server",this_client, name + " is successfully added as your friend",None,None)

                                    self.profiles[user.username].addFriend(client_socket, username)
                                    self.send_msg("server",(user.socket,user.username), username + " is successfully added as your friend",None,None)
                                    value = 1
                                    break
                            
                            if value == 0 :
                                self.send_msg("server",this_client,"There is no profile with username : " + name,None,None)
                        else:
                            self.send_msg("server",this_client,"Please input the username",None,None)

                    # Konfigurasi Room
                    elif(req.message[0] == "!listroom"):
                        listroom = dict(self.listRoom())
                        i=0
                        msg = ''
                        while i < len(listroom):
                            msg += "Room " + str(i) + " : "
                            msg += str(listroom[i])
                            i+=1
                            msg += '\n'
                        if len(listroom)>0:
                            self.send_msg("server",this_client,msg,None,None)
                        else:
                            self.send_msg("server",this_client,"There is no room in this server. Let's create room!",None,None)

                    elif(req.message[0] == "!createroom"):
                        if len(self.rooms) < 3:
                            self.createRoom()
                            self.send_msg("server",this_client,"Room is created successfully",None,None)
                        else:
                            self.send_msg("server",this_client,"Maximum room quota (3) is exceeded",None,None)

                    elif(req.message[0] == "!play"):
                        temp = self.checkRoom(self.profiles[username].room)
                        if temp == 0:
                            self.send_msg("server",this_client,"Room is not ready",None,None)
                    
                    elif(req.message[0] == "!enterroom"):
                        if len(req.message) > 1:
                            index = int(req.message[1])
                            if index < len(self.rooms):
                                print("index = " + str(index))
                                temp = self.rooms[index].addPlayer(username, client_socket)
                                if temp == True:
                                    self.send_msg("server",this_client,"You entered room " + str(index),None,None)
                                    print(username + " enter room " + str(index))
                                    if self.profiles[username].room != -1:
                                        self.rooms[self.profiles[username].room].removePlayer(client_socket)
                                    self.profiles[username].room = index
                                    # self.checkRoom(index)
                                else:
                                    self.send_msg("server",this_client,"Room is not available",None,None)

                            else:
                                self.send_msg("server",this_client,"Room not found!",None,None)

                        else:
                            self.send_msg("server",this_client,"Please input the room number!",None,None)
                    
                    # Pengiriman Pesan
                    elif(req.message[0] == "!send"):
                        if(req.message[1] == "-b"):
                            if len(req.message) > 2:
                                pesan = req.message[2]
                            else:
                                pesan = ''     

                            for client_sock,client_uname in self.clients.items():
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
                                if len(req.message) > 3:
                                    self.send_msg(this_client[1],(keys[0],req.message[2]),req.message[3],None,None)
                                
                                else:
                                    self.send_msg("server",this_client,"Masukkan pesan anda",None,None)
                        
                        elif(req.message[1] == "-a"):
                            for client_sock,client_uname in self.profiles[username].friend.items():
                                if len(req.message)>2:
                                    pesan = req.message[2]
                                    if(len(req.message)==4):
                                        pesan += " "+req.message[3]
                                else:
                                    pesan = ''
                                self.send_msg("FRIENDS/"+username,(client_sock,client_uname),pesan,None,None)

                        elif(req.message[1] == "-ft"):
                            value = 0
                            for client_sock,client_uname in self.profiles[username].friend.items():
                                if(client_uname == req.message[2]):
                                    pesan = "file transfer"

                                    if len(req.message) > 3:
                                        filename = req.message[3]
                                        data = req.attachment
                                        self.send_msg("FRIENDS/"+username,(client_sock,client_uname),pesan,filename,data)
                                        value = 1
                                    
                                    else:
                                        self.send_msg("server",this_client,"Please input filename",None,None)
                            
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



