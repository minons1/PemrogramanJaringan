class Message():
    def __init__(self,sender,receiver,message,filename,attachment):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.filename = None
        self.attachment = None

    def load_file(self,filename):
        pass
        # to-do
    
    def save_file(self,filename):
        pass
        # to-do

COMMAND_AVAILABLE = {
      "!help" : "help",
      "!exit" : "exit messanger",
      "!send" : "send message\n\t-f [name] for private message\n\t-b for broadcast message\n\t-a [name] for add friends\n\t-ft [name] [filename] for send file to added friend"
}