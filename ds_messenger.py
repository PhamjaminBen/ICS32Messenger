# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

from os import terminal_size, write
from typing import TextIO
import ds_client as dsc
import time, socket, json
from json.decoder import JSONDecodeError
import ds_protocol as dsp

class DirectMessage:
  '''
  DirectMessage class stores data pertaining to a direct message
  '''
  def __init__(self,recipient = None, message = None, timestamp = None):
    self.recipient = recipient
    self.message = message
    self.timestamp = timestamp

  def __repr__(self) -> str:
      return f"Recipient: {self.recipient}, Message: {self.message}, Timestamp: {self.timestamp}"


class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
    self.token = None
    self.dsuserver = dsuserver
    self.username = username
    self.password = password
    self.token = None
    self.f_recv = None
    self.f_send = None
		

  def send(self, message:str, recipient:str) -> bool:
    '''
    Connects to the server using a socket, and attempts to send a message
    returns true if message successfully sent, false if send failed.
    '''
    self.log_in()
    message = DirectMessage(recipient,message, time.time())
    
    if not self._write_command(dsp.encode_json("directmessage", message.message,message.recipient, message.timestamp, self.token), self.f_send):
      print(self._read_command(self.f_recv))
      return False
    else:
      print(self._read_command(self.f_recv))
      return True
    

  def log_in(self):
    '''
    logs account into the server
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5) #If socket can't connect in 5 seconds, error will be thrown

    #connecting to server, encoding is automatically done through these files
    try:
      client.connect((self.dsuserver,3021))
      self.f_send = client.makefile('w')
      self.f_recv = client.makefile('r')
    except socket.error:
      print("ERROR: Invalid socket connection/ip address")
      return False
    
    if not self._write_command(dsp.encode_json("join", self.username,self.password), self.f_send): return False
    self.token = self._read_command(self.f_recv)
    if self.token == "": return False



  def _read_command(self,f_recv, login = True, get_all = False):
    '''
    reads from the server and extracts the message, returns user token if logged in
    if login is true, will print the message
    if get_all is true, will return the entire object
    '''
    s = dsp.extract_json(self.f_recv.readline()[:-1])
    if login: print("[SERVER MESSAGE]", s.type+ ":", s.message)
    if get_all: return s
    else: return s.token


  def _write_command(self,cmd: str, f_send) -> bool:
    '''
    sends data to server using json
    '''
    try:
        self.f_send.write((json.dumps(cmd) + "\r\n"))
        self.f_send.flush()
        return True
    except JSONDecodeError:
        print("ERROR: Could not write to output file")
    return False 
		


  def retrieve_new(self) -> list:
    '''
    returns a list of DirectMessage objects containing all new messages
    '''
    self.log_in()

    #populate the DirectMessages list with all new ones
    DirectMessages = []
    self._write_command(dsp.encode_json("unread_message", token = self.token), self.f_send)
    s = self._read_command(self.f_recv, get_all= True).message
    for message in s:
      DirectMessages.append(DirectMessage(self.username, message['message'], message['timestamp']))

    return DirectMessages

    
 
  def retrieve_all(self) -> list:
    # returns a list of DirectMessage objects containing all messages
    pass

if __name__ == "__main__":
    messenger = DirectMessenger("168.235.86.101", "username", "password")
    print(messenger.send("hello","benP"))
    print(messenger.send("shut up","benP"))
    print(messenger.send("wfaf","benP"))
    print(messenger.send("giojoeig","benP"))
    print(messenger.send("POOP","benP"))
    messenger = DirectMessenger("168.235.86.101", "benP", "waytomad")
    print(messenger.send("hi","username"))
    for message in messenger.retrieve_new():
      print(message)