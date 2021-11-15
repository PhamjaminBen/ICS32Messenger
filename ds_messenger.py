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
  def __init__(self,recipient = None, message = None, timestamp = None):
    self.recipient = recipient
    self.message = message
    self.timestamp = timestamp


class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
    self.token = None
    self.dsuserver = dsuserver
    self.username = username
    self.password = password
		
  def send(self, message:str, recipient:str) -> bool:
    # returns true if message successfully sent, false if send failed.
    message = DirectMessage(recipient,message, time.time())

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5) #If socket can't connect in 5 seconds, error will be thrown

    #connecting to server, encoding is automatically done through these files
    try:
      client.connect((self.dsuserver,3021))
      f_send = client.makefile('w')
      f_recv = client.makefile('r')
    except socket.error:
      print("ERROR: Invalid socket connection/ip address")
      return False
    
    if not self._write_command(dsp.encode_json("join", self.username,self.password), f_send): return False
    token = self._read_command(f_recv)
    if token == "": return False
    
    if not self._write_command(dsp.encode_json("directmessage", message.message,message.recipient, message.timestamp, token), f_send):
        print(self._read_command(f_recv))
        return False
    else:
        print(self._read_command(f_recv))
        return True
    
  def _read_command(self,f_recv, login = True) -> str:
    '''
    reads from the server and extracts the message, returns user token if logged in
    if login is true, will print the message
    '''
    s = dsp.extract_json(f_recv.readline()[:-1])
    if login: print("[SERVER MESSAGE] " + s.type + ": " + s.message)
    return s.token


  def _write_command(self,cmd: str, f_send) -> bool:
    '''
    sends data to server using json
    '''
    try:
        f_send.write((json.dumps(cmd) + "\r\n"))
        f_send.flush()
        return True
    except JSONDecodeError:
        print("ERROR: Could not write to output file")
    return False 
		


  def retrieve_new(self) -> list:
    # returns a list of DirectMessage objects containing all new messages
    pass
 
  def retrieve_all(self) -> list:
    # returns a list of DirectMessage objects containing all messages
    pass

if __name__ == "__main__":
    messenger = DirectMessenger("168.235.86.101", "username", "password")
    print(messenger.send("hello","benP"))
    messenger = DirectMessenger("168.235.86.101", "benP", "waytomad")
    print(messenger.send("hi","username"))