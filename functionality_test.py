from time import time
import ds_protocol as dsp
from Profile import Profile
from ds_messenger import DirectMessage, DirectMessenger
import ds_client as dsc
import time


# messenger = DirectMessenger("168.235.86.101", "username", "password")
# messenger.send("hello","benP")
# messenger.send("shut up","benP")
testprofile = Profile("168.235.86.101", "benP", "waytomad")
testprofile.recipients
print(testprofile.recipients)
testprofile.save_profile("C:/Users/BPPC/Downloads/FINALTEST/tester.dsu")


testprofile2 = Profile()
testprofile2.load_profile("C:/Users/BPPC/Downloads/FINALTEST/tester.dsu")
print(testprofile2.recipients)