from time import time
import ds_protocol as dsp
from Profile import Profile, Sender, Post
from ds_messenger import DirectMessage, DirectMessenger
import ds_client as dsc
import time


messenger = DirectMessenger("168.235.86.101", "username", "password")
messenger.send("hello","benP")
messenger.send("shut up","benP")
testprofile = Profile("168.235.86.101", "benP", "waytomad")
reciever = DirectMessenger("168.235.86.101", "benP", "waytomad")
for message in reciever.retrieve_new():
  if message.sender not in testprofile.senders:
    testprofile.senders[message.sender] = []
  testprofile.senders[message.sender].append(message)

benny = Sender("hello",[DirectMessage("benp","hello", time.time(), "hello")],[])
testprofile.save_profile("C:/Users/BPPC/Downloads/FINALTEST/tester.dsu")
print("recipitne:", testprofile.get_senders())


testprofile2 = Profile()
testprofile2.load_profile("C:/Users/BPPC/Downloads/FINALTEST/tester.dsu")
print(testprofile.get_senders())