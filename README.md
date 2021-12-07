Welcome to the final project for ICS32 By Benjamin Pham

Instructions:
  The main program is run by executing the __main.py__ file, a popup window will appear.
  The cascading menu on top gives you options to either create a new file, open a previous one, or look at the statistics between users (currently selected user)
    When creating a new file, the name of the file will be the username of the user.
  In order to send a message to another user, you must click on their name on the node tree first, which will display the message history between you
  To add a sender (aka another user), click the "add sender" button on the bottom right, which will prompt you to enter their username
  To send a message, type the desired message in the bottom text box, and then hit the "send" button

Flourish Added: 
  I added a "statistics" option to the cascading menu, that will show the stats between the two users such as the first and latest message and # of messages

Custom Class added: 
  I added the Sender Class in __Profile.py__ that is meant to represent another user that the current profile is interacting with, includes messages sent to and from the sender

Custom Exception added: 
  I added the DsuClientError in __ds_messenger.py__ that is raised when there are problems with server connection or data sending to a server
