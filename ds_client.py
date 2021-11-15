# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

from json.decoder import JSONDecodeError
import socket
from typing import TextIO
import ds_protocol as dsp
import time
import json

def send(server:str, port:int, username:str, password:str, message:str, bio:str=None):
  '''
  The send function joins a ds server and sends a message, bio, or both

  :param server: The ip address for the ICS 32 DS server.
  :param port: The port where the ICS 32 DS server is accepting connections.
  :param username: The user name to be assigned to the message.
  :param password: The password associated with the username.
  :param message: Optional: The message to be sent to the server.
  :param bio: Optional, a bio for the user.
  '''

  # Ensures correct types for each variable
  if type(port) != int or type(server) != str\
      or  type(username) != str or  type(password) != str or\
      not (type(message) == str or message == None) or \
      not (type(bio) == str or bio == None):
    print("ERROR: Invalid input type(s)")
    return
  
  if message == "":
    print("ERROR: Can not send an empty message")
    return

  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.settimeout(5) #If socket can't connect in 5 seconds, error will be thrown
  
  #connecting to server, encoding is automatically done through these files
  try:
    client.connect((server,port))
    f_send = client.makefile('w')
    f_recv = client.makefile('r')
  except socket.error:
    print("ERROR: Invalid socket connection/ip address")
    return
  
  #ensuring proper user login, making sure bio/post is updated only when given
  if not _write_command(dsp.encode_json("join",username,password),f_send): return

  if message == None and bio == None: 
    print(f"Connected to {port} on {server}")
    return _read_command(f_recv,True)
  else: 
    token = _read_command(f_recv,False)

  if token == "": 
    return

  if message != None:
    _write_command(dsp.encode_json("post",message, time.time(),token),f_send)
    _read_command(f_recv)
  if bio != None:
    _write_command(dsp.encode_json("bio",bio,time.time(),token),f_send)
    _read_command(f_recv)


def _read_command(f_recv: TextIO, login = True) -> str:
    '''
    reads from the server and extracts the message, returns user token if logged in
    if login is true, will print the message
    '''
    s = dsp.extract_json(f_recv.readline()[:-1])
    if login: print("[SERVER MESSAGE] " + s.type + ": " + s.message)
    return s.token

def _return_response(f_recv: TextIO):
    return dsp.extract_json(f_recv.readline()[:-1])


def _write_command(cmd: str, f_send: TextIO) -> bool:
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