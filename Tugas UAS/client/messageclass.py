import pickle

class Message():
    def __init__(self,sender,receiver,message,filename,attachment):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.filename = filename
        self.attachment = attachment

    def load_file(self,filename):
        pass
        # to-do
    
    def save_file(self,filename):
        pass
        # to-do

COMMAND_AVAILABLE = {
      "!help" : "help",
      "!exit" : "exit messanger",
      "!addfriend" : "-[username] add username as a friend",
      "!friendlist" : "show friendlist",
      "!listroom"   : "show roomlist",
      "!createroom"   : "create a room",
      "!enterroom"   : "-[roomNumber] enter a room [roomNumber]",
      "!play"    : "ask room to play the game (must entered any room first)",
      "left"    : "choose left side",
      "right"   : "choose right side",
      "leave"     : "leave room",
      "!send" : "send message\n\t-f [name] for private message\n\t-b for broadcast message\n\t-a [name] for send message to added friend\n\t-c for room message \n\t-ft [name] [filename] for send file to added friend"
}