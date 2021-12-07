# Profile.py
#
# ICS 32 Fall 2021
# Assignment #2: Journal
#
# Author: Mark S. Baldwin
#
# v0.1.7

# You should review this code to identify what features you need to support
# in your program for assignment 2.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THE JSON SERIALIZATION ASPECTS OF THIS CODE RIGHT NOW, 
# though can you certainly take a look at it if you are curious.
#

#CHANGED BY BENJAMIN PHAM FOR FINAL PROJECT
# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

import json, time, os
from pathlib import Path
from typing import List
from ds_messenger import DirectMessage

class DsuFileError(Exception):
    """
    DsuFileError is a custom exception handler that is raised when attempting to load or save Profile objects to file the system.
    """
    pass

class DsuProfileError(Exception):
    """
    DsuProfileError is a custom exception handler that is raised when attempting to deserialize a dsu file to a Profile object.
    """
    pass


class Post(dict):
    """ 
    The Post class is responsible for working with individual user posts. 
    """
    def __init__(self, entry:str = None, timestamp:float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)

        # Subclass dict to expose Post properties for serialization
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)
    
    def set_entry(self, entry):
        self._entry = entry 
        dict.__setitem__(self, 'entry', entry)

        # If timestamp has not been set, generate a new from time module
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        return self._entry
    
    def set_time(self, time:float):
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)
    
    def get_time(self):
        return self._timestamp

    """

    The property method is used to support get and set capability for entry and time values.
    When the value for entry is changed, or set, the timestamp field is updated to the
    current time.

    """ 
    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)

class Sender(dict):
  '''
  Sender class has the role of saving those who the current profile sends messages to
  Keep track of both messages recieved and messages sent
  '''

  def __init__(self, name: str, messages: list[DirectMessage], sent: list[DirectMessage]):
    self.messages = messages
    self.name = name
    self.sent = sent
    dict.__init__(self, name = self.name, messages = self.messages, sent = self.sent)
  
  def add_message(self, message: DirectMessage):
    '''
    adds a message to the list of recieved messages
    '''
    self.messages.append(message)
    dict.__setitem__(self, 'messages', self.messages)
  
  def add_sent(self, message: DirectMessage):
    '''
    adds a message to the list of sent messages
    '''
    self.sent.append(message)
    dict.__setitem__(self,'sent',self.sent)

    
    
class Profile:
    """
    The Profile class exposes the properties required to message other users
    """

    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver # REQUIRED: Server that messages are sent on
        self.username = username # REQUIRED
        self.password = password # REQUIRED
        self.senders = {}     #list of other users you have direct messages with
    
    def get_senders(self) -> list[Sender]:
      '''
      returns the list containing all senders associated with the profile
      '''
      return self.senders

    def save_profile(self, path: str) -> None:
        """
        save_profile accepts an existing dsu file to save the current instance of Profile to the file system.

        Example usage:

        profile = Profile()
        profile.save_profile('/path/to/file.dsu')

        Raises DsuFileError
        """
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'w')
                json.dump(self.__dict__, f)
                f.close()
            except Exception as ex:
                raise DsuFileError("An error occurred while attempting to process the DSU file.", ex)
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """

        load_profile will populate the current instance of Profile with data stored in a DSU file.

        Example usage: 

        profile = Profile()
        profile.load_profile('/path/to/file.dsu')

        Raises DsuProfileError, DsuFileError

        """
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                for sender in obj['senders'].keys():
                    list1 = []
                    for message in obj['senders'][sender]['messages']:
                      list1.append(DirectMessage(message['recipient'],message['message'], message['timestamp'], message['sender']))
                    
                    list2 = [] #we initialize two separate lists to avoid object referencing referring to the same object
                    for message in obj['senders'][sender]['sent']:
                        list2.append(DirectMessage(message['recipient'],message['message'], message['timestamp'], message['sender']))
                    self.senders[sender] = Sender(sender,list1,list2)
                f.close()
            except AttributeError as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()


