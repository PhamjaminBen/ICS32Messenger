# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

from os import terminal_size, write
from typing import Any, TextIO
import time, socket, json
from json.decoder import JSONDecodeError
import ds_protocol as dsp

class DsuClientError(Exception):
    """
    DsuClientError is a custom exception handler that is raised when there are problems with server connection or data sending to a server
    """
    pass

class DirectMessage(dict):
  '''
  DirectMessage class stores data pertaining to a direct message
  '''
  def __init__(self,recipient:str = None, message:str = None, timestamp:float = None, sender:str = None):
    self.recipient = recipient
    self.message = message
    self.timestamp = timestamp
    self.sender = sender
    #ensures it can be stored using json
    dict.__init__(self, recipient = self.recipient, message = self.message, timestamp = self.timestamp, sender = self.sender)

  def __repr__(self) -> str:
      return f"Recipient: {self.recipient}, Message: {self.message}, Timestamp: {self.timestamp}, Sender: {self.sender}"


class DirectMessenger:
  '''
  DirectMessenger class represents a user who is using the messenging platform
  '''
  def __init__(self, dsuserver:str = None, username:str = None, password:str = None):
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
    if not self.log_in(): return False
    message = DirectMessage(recipient,message, time.time())
  
    if not self._write_command(dsp.encode_json("directmessage", message.message,message.recipient, message.timestamp, self.token), self.f_send):
      print(self._read_command(self.f_recv))
      self.client.close()
      return False
    else:
      print(self._read_command(self.f_recv))
      self.client.close()
      return True
    

  def log_in(self) -> bool:
    '''
    logs account into the server
    returns True if succesful login, false otherwise
    '''
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.settimeout(5) #If socket can't connect in 5 seconds, error will be thrown

    #connecting to server, encoding is automatically done through these files
    try:
      self.client.connect((self.dsuserver,3021))
      self.f_send = self.client.makefile('w')
      self.f_recv = self.client.makefile('r')
    except socket.error as ex:
      raise DsuClientError("Problem logging into the server",ex)
    
    if not self._write_command(dsp.encode_json("join", self.username,self.password), self.f_send): return False
    self.token = self._read_command(self.f_recv, login = False)
    if self.token == "": return False
    return True



  def _read_command(self,f_recv, login = True, get_all = False) -> Any:
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
    Sends data to server in json format
    '''
    try:
        self.f_send.write((json.dumps(cmd) + "\r\n"))
        self.f_send.flush()
        return True
    except JSONDecodeError as ex:
        raise DsuClientError("Error while Sending JSOn to server", ex)
		


  def retrieve_new(self) -> list:
    '''
    returns a list of DirectMessage objects containing all new messages
    '''
    if not self.log_in():
      return []

    #populate the new_messages list with all new ones
    new_messages = []
    self._write_command(dsp.encode_json("unread_message", token = self.token), self.f_send)
    s = self._read_command(self.f_recv, login = False,get_all= True).message
    for message in s:
      new_messages.append(DirectMessage(self.username, message['message'], message['timestamp'], message['from']))

    self.client.close()
    return new_messages

    
 
  def retrieve_all(self) -> list:
    '''
    returns a list of DirectMessage objects containing all messages
    '''
    if not self.log_in():
      return []
    
    #populate all messages list
    all_messages = []
    self._write_command(dsp.encode_json("all_messages", token = self.token), self.f_send)
    s = self._read_command(self.f_recv, get_all= True).message
    for message in s:
      all_messages.append(DirectMessage(self.username, message['message'],message['timestamp'], message['from']))
    
    self.client.close()
    return all_messages