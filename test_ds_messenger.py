import unittest
from ds_messenger import DirectMessenger, DirectMessage 
import time

class CommandTestBase(unittest.TestCase):

  def test_direct_message(self):
    '''
    simply tests if initialization works correctly
    '''
    t = time.time()
    dm = DirectMessage("Ben", "hello", t)
    self.assertEqual([dm.recipient, dm.message, dm.timestamp], ["Ben", "hello", t])

  def test_direct_messenger(self):
    #sending to an invalid server
    sender = DirectMessenger("invalidserver", "username", "password")
    self.assertEqual(False,sender.send("hello","benP"))

    #sending to valid server
    sender = DirectMessenger("168.235.86.101", "username", "password")
    self.assertEqual(True, sender.send("hello", "benP"))
    sender.send("goodbye", "benP")

    #retrieving new messages
    rcvr = DirectMessenger("168.235.86.101", "benP", "waytomad")
    new_msgs = rcvr.retrieve_new()
    self.assertEqual(new_msgs[0].recipient, "benP")
    self.assertEqual(new_msgs[1].message, "goodbye")

    #sending new message
    sender.send("33", "benP")

    new_msgs2 = rcvr.retrieve_new()
    self.assertEqual(new_msgs2[0].message, "33")
    self.assertEqual(new_msgs2[0].recipient, "benP")

    all_msgs = rcvr.retrieve_all()
    self.assertEqual(all_msgs[0].message, "hello")
    self.assertEqual(all_msgs[-1].message, "33")



if __name__ == "__main__":
  unittest.main()