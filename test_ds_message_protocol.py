# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

import ds_protocol, unittest

class CommandTestBase(unittest.TestCase):

  def test_encode_json(self):
    t1 = ds_protocol.encode_json("join","username","password")
    self.assertEqual(t1,{"join": {"username": "username","password": "password","token":""}})

    t1 = ds_protocol.encode_json("post","entry1","entry2",token="token")
    self.assertEqual(t1,{"token":"token", "post": {"entry": "entry1","timestamp": "entry2"}})

    t1 = ds_protocol.encode_json("bio","entry1","entry2",token="token")
    self.assertCountEqual(t1,{"token":"token", "bio": {"entry": "entry1","timestamp": "entry2"}})

    t1 = ds_protocol.encode_json("directmessage","entry1","entry2","entry3",token="token")
    self.assertEqual(t1,{"token":"token", "directmessage": {"entry":"entry1", "recipient":"entry2", "timestamp": "entry3"}})

    t1 = ds_protocol.encode_json("unread_message", token = "token")
    self.assertEqual(t1,{"token":"token", "directmessage": "new"})

    t1 = ds_protocol.encode_json("all_messages",token = "token")
    self.assertEqual(t1,{"token":"token", "directmessage": "all"})
  
  def test_extract_json(self):
    d1 = ds_protocol.extract_json("{\"response\": {\"type\": \"ok\", \"message\": \"Direct message sent\"}}")
    self.assertEqual(d1, ds_protocol.response("ok", "Direct message sent", ""))

    d1 = ds_protocol.extract_json("{\"response\": {\"type\": \"ok\", \"messages\": [{\"message\":\"Hello User 1!\", \"from\":\"markb\", \"timestamp\":\"1603167689.3928561\"},{\"message\":\"Bzzzzz\", \"from\":\"thebeemoviescript\", \"timestamp\":\"1603167689.3928561\"}]}}")
    self.assertEqual(d1, ds_protocol.response("ok", {'message': 'Hello User 1!', 'from': 'markb', 'timestamp': '1603167689.3928561'}, {'message': 'Bzzzzz', 'from': 'thebeemoviescript', 'timestamp': '1603167689.3928561'},""))

if __name__ == '__main__':
  unittest.main()

