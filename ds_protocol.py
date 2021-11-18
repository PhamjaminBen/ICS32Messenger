# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186

import json,time
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
response = namedtuple('response', ['type','message','token'])

def extract_json(json_msg:str) -> response:
  '''
  Call the json.loads function on a json string and convert it to a DataTuple object
  '''
  try:
    json_obj = json.loads(json_msg)
  except json.JSONDecodeError:
    print("Json cannot be decoded.")
    return
  try:
    type = json_obj['response']['type']
    message = json_obj['response']['message']
    try:
      token = json_obj['response']['token']
    except KeyError:
      token = ""
  except KeyError:
    message = json_obj['response']['messages']
    token = ""

  return response(type, message,token)

def encode_json(type: str, entry1 = "", entry2 = "", entry3 = "", token = None) -> dict:
  '''
  Takes a input type and creates json dictionary response using other entries
  '''
  try:
    match type:
      case "join":
        return {"join": {"username": entry1,"password": entry2,"token":""}}
      
      case "post":
        return {"token":token, "post": {"entry": entry1,"timestamp": entry2}}
      
      case "bio":
        return {"token":token, "bio": {"entry": entry1,"timestamp": entry2}}
      
      case "directmessage":
        return {"token":token, "directmessage": {"entry":entry1, "recipient":entry2, "timestamp": entry3}}
      
      case "unread_message":
        return {"token":token, "directmessage": "new"}
      
      case "all_messages":
        return {"token":token, "directmessage": "all"}
      
      case _:
        return("ERROR: Not a valid server command")
    
  except TypeError:
    print("ERROR: Incorrect Entry Types")
    return None

if __name__ == "__main__":
  print(encode_json("unread_message", token = "token"))
  print(extract_json("{\"response\": {\"type\": \"ok\", \"messages\": [{\"message\":\"Hello User 1!\", \"from\":\"markb\", \"timestamp\":\"1603167689.3928561\"},{\"message\":\"Bzzzzz\", \"from\":\"thebeemoviescript\", \"timestamp\":\"1603167689.3928561\"}]}}"))
