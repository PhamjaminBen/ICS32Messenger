# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

from json.decoder import JSONDecodeError
import socket
from typing import TextIO
import ds_protocol as dsp
import time
import json

class DsuClientError(Exception):
    """
    DsuClientError is a custom exception handler that is raised when there are problems with server connection or data sending to a server
    """
    pass

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
  
  if message == "":
    raise DsuClientError("Invalid Message to Send to DSU Server")

  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.settimeout(5) #If socket can't connect in 5 seconds, error will be thrown
  
  #connecting to server, encoding is automatically done through these files
  try:
    client.connect((server,port))
    f_send = client.makefile('w')
    f_recv = client.makefile('r')
  except socket.error as ex:
    raise DsuClientError("Invalid socket connection",ex)
  
  #ensuring proper user login, making sure bio/post is updated only when given
  if not write_command(dsp.encode_json("join",username,password),f_send): return

  if message == None and bio == None: 
    print(f"Connected to {port} on {server}")
    return read_command(f_recv,True)
  else: 
    token = read_command(f_recv,False)

  if token == "": 
    return

  if message != None:
    write_command(dsp.encode_json("post",message, time.time(),token),f_send)
    read_command(f_recv)
  if bio != None:
    write_command(dsp.encode_json("bio",bio,time.time(),token),f_send)
    read_command(f_recv)


def read_command(f_recv: TextIO, login = True) -> str:
    '''
    reads from the server and extracts the message, returns user token if logged in
    if login is true, will print the message
    '''
    s = dsp.extract_json(f_recv.readline()[:-1])
    if login: print("[SERVER MESSAGE] " + s.type + ": " + s.message)
    return s.token


def write_command(cmd: str, f_send: TextIO) -> bool:
  '''
  sends data to server using json
  '''
  try:
    f_send.write((json.dumps(cmd) + "\r\n"))
    f_send.flush()
    return True
  except JSONDecodeError as ex:
    raise DsuClientError("Error while sending JSON data to the server.",ex)
    return False 