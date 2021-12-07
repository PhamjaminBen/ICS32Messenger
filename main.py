
# a5.py
# 
# ICS 32 
#
# v0.4
# 
# The following module provides a graphical user interface shell for the DSP journaling program.

# MODIFIED BY BENJAMIN FOR FINAL PROJECT
# BENJAMIN PHAM
# BENJADP1@UCI.EDU
# 53569186


from json.decoder import JSONDecodeError
from os import error
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, Label
from tkinter.constants import N, NO, W
from typing import Text
from Profile import Post, Profile, Sender
import time
from ds_messenger import DirectMessenger, DirectMessage, DsuClientError
from pathlib import Path
import datetime


class Body(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the body portion of the root frame.
    """
    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # a list of the sender objects available in the active DSU file
        self._senders = []
        
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Body instance 
        self._draw()
    
    def node_select(self, event):
        """
        Update the entry_editor with the full post entry when the corresponding node in the senders_tree
        is selected.
        """
        try:
          self.current_index = int(self.senders_tree.selection()[0])
        except IndexError:
          return #catches error when first opening file
        sender  = self._senders[self.current_index]
        self.process_messages(sender)

    def process_messages(self, sender: Sender):
      '''
      Refreshes the text entry of the selected Sender
      Recreates the message history between client and respective sender using timestamps
      '''
      self.set_text_entry(" ")
      entry = ""
      idx1 = 0
      idx2 = 1 #ignores the initialization message for the sent list
      
      while idx1 < len(sender.messages) and idx2 < len(sender.sent):
        if float(sender.messages[idx1].timestamp) < float(sender.sent[idx2].timestamp):
          entry += f'{sender.name}: {sender.messages[idx1].message}\n'
          idx1 += 1
        else: 
          entry += f'{sender.sent[idx2].sender}: {sender.sent[idx2].message}\n'
          idx2 += 1
      
      #displays the remaining messages when one or the other has all of theirs displayed
      if idx1 == len(sender.messages):
        for x in range(idx2,len(sender.sent)):
          entry += f'{sender.sent[x].sender}: {sender.sent[x].message}\n'
      else:
        for x in range(idx1,len(sender.messages)):
          entry += f'{sender.name}: {sender.messages[x].message}\n'
      self.set_text_entry(entry)

    def get_text_entry(self) -> str:
        """
        Returns the text that is currently displayed in the entry_editor widget.
        """
        return self.entry_editor.get('1.0', 'end').rstrip()


    def set_text_entry(self, text:str):
      """
      Sets the text to be displayed in the entry_editor widget.
      NOTE: This method is useful for clearing the widget, just pass an empty string.
      """
      self.entry_editor.replace("1.0","end", text)
    
    def set_senders(self, senders:list):
        """
        Populates the self._senders attribute with Senders from the active DSU file.
        """
        for sender in senders:
            self._senders = []
            for item in self.senders_tree.get_children():
                self.senders_tree.delete(item)
            self.insert_sender(sender)
            
    def insert_sender(self, sender: Sender):
        """
        Inserts a single sender to the post_tree widget.
        """
        self._senders.append(sender)
        id = len(self._senders) - 1 #adjust id for 0-base of treeview widget
        self._insert_sender_tree(id, sender.name)

    def reset_ui(self):
        """
        Resets all UI widgets to their default state. Useful for when clearing the UI is neccessary such
        as when a new DSU file is loaded, for example.
        """
        self.set_text_entry("")
        self.entry_editor.configure(state=tk.NORMAL)
        self._senders = []
        for item in self.senders_tree.get_children():
            self.senders_tree.delete(item)

    def _insert_sender_tree(self, id, sender):
        """
        Inserts a sender entry into the senders_tree widget.
        """
        #if sendername is too long, then cut if off
        if len(sender) > 25:
            sender = sender[:24] + "..."
        
        self.senders_tree.insert('', id, id, text=sender)
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.senders_tree = ttk.Treeview(posts_frame)
        self.senders_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.senders_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=0)

        entry_frame = tk.Frame(master=self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        editor_frame = tk.Frame(master=entry_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        scroll_frame = tk.Frame(master=entry_frame, bg="blue", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        
        self.entry_editor = tk.Text(editor_frame, width=0)
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=0, pady=0)

        entry_editor_scrollbar = tk.Scrollbar(master=scroll_frame, command=self.entry_editor.yview)
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)



class Footer(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the footer portion of the root frame.
    """
    def __init__(self, root, save_callback=None, sender_callback = None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._save_callback = save_callback
        self._sender_callback = sender_callback

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Footer instance 
        self._draw()
    
    def sender_click(self):
        """
        Calls the callback function specified in the sender class attribute, if
        available, when the add sender button has been clicked.
        """
        if self._sender_callback is not None:
            self._sender_callback()

    def send_click(self):
        """
        Calls the callback function specified in the save_callback class attribute, if
        available, when the save_button has been clicked.
        """
        if self._save_callback is not None:
            self._save_callback()
    
    def get_entry(self) -> str:
        '''
        Retrieves the current entry in the message box
        '''
        return self.message_box.get('1.0', 'end').rstrip()
    
    def set_entry(self, entry:str):
        '''
        Changes the entry of the message box
        '''
        self.message_box.replace("1.0","end", entry)

    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        save_button = tk.Button(master=self, text="Send", width=12, height= 20)
        save_button.configure(command=self.send_click)
        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx =0, pady=50)

        sender_button = tk.Button(master=self, text = "Add sender", width = 12, height= 20)
        sender_button.configure(command= self.sender_click)
        sender_button.pack(fill=tk.BOTH, side=tk.TOP, padx =5, pady=50)

        self.message_box = tk.Text(height= 5, width= 49)
        self.message_box.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=10, pady=10)


class MainApp(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the main portion of the root frame. Also manages all method calls for
    the NaClProfile class.
    """
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        # Initialize a new Profile and assign it to a class attribute.
        self._current_profile = Profile()

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the root frame
        self._draw()

    def error_win(self, error):
        '''
        Window popup intended to inform users about errors
        '''
        win = tk.Toplevel(main)
        win.title("Error")
        win.geometry('600x100')
        Label(win, text="ERROR").pack()

        #draws window with the error message
        self.error_text = tk.Label(win, text=error)
        self.error_text.pack(fill=tk.BOTH, side=tk.TOP)
    
    def stat_win(self):
      '''
      Window popup intended to inform user about stats between senders
      '''
      try:
        current_index = int(self.body.senders_tree.selection()[0])
        sender  = self.body._senders[current_index]
      except IndexError:
        self.error_win("No sender currently selected")
        return
      
      #calculating the first message sent, by seeing which timestamp is most ancient
      t1 = 999999999999999.0
      t2 = 999999999999999.0
      mintime = None
      minmsg1 = None
      minmsg2 = None
      try:
        t1 = float(sender.sent[1].timestamp)
      except IndexError: pass
      try:
        t2 = float(sender.messages[0].timestamp)
      except IndexError: pass

      print(t1,t2)

      if min(t1,t2) == 999999999999999.0:
        mintime = "None"
        minmsg1 = "None"
        minmsg2 = "None"
      else: 
        mintime = datetime.datetime.fromtimestamp(min(t1,t2))
        if t1 < t2:
          minmsg1 = sender.sent[1].message
          minmsg2 = sender.sent[1].sender
        else:
          minmsg1 = sender.messages[0].message
          minmsg2 = sender.messages[0].sender

      #calculating the latest message sent, by seeing which timestamp is most recent
      t1 = 0.0
      t2 = 0.0
      maxtime = None
      maxmsg1 = None
      maxmsg2 = None
      try:
        if len(sender.sent) != 1:
          t1 = float(sender.sent[-1].timestamp)
      except IndexError: pass
      try:
          t2 = float(sender.messages[-1].timestamp)
      except IndexError: pass

      if max(t1,t2) == 0.0:
        maxtime = "None"
        maxmsg1 = "None"
        maxmsg2 = "None"
      else: 
        maxtime = datetime.datetime.fromtimestamp(max(t1,t2))
        if t1 > t2:
          maxmsg1 = sender.sent[-1].message
          maxmsg2 = sender.sent[-1].sender
        else:
          maxmsg1 = sender.messages[-1].message
          maxmsg2 = sender.messages[-1].sender


      #Displying info on a popup window
      win = tk.Toplevel(main)
      win.title("Stats")
      win.geometry('400x200')
      Label(win, text = "STATS").pack

      label = f"""
      STATISTICS WITH: {sender.name}

      Total messages exchanged: {len(sender.messages) + len(sender.sent)-1}
      Messages sent by you: {len(sender.sent)-1}
      Messages sent by {sender.name}: {len(sender.messages)}
      First message: {minmsg1}, from {minmsg2}
      First message time: {mintime}
      Latest message: {maxmsg1}, from {maxmsg2}
      Latest message time: {maxtime}
      """

      self.text = tk.Label(win,text = label)
      self.text.pack(fill=tk.BOTH, side=tk.TOP)
    
    def new_profile(self):
        """
        Creates a new DSU file when the 'New' menu item is clicked.
        Autogenerates username and password according to file name
        """
        #makes it so that user doesn't need to enter file extension
        filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')],defaultextension=".dsu")
        try:
          self.profile_filename = filename.name
        except AttributeError:return #catches error if user exits file selection

        self.body.reset_ui()
        self._current_profile = Profile()

        #autogenerates username and password
        name = self.profile_filename[self.profile_filename.rfind("/")+1:-4]
        self._current_profile.username = name
        self._current_profile.password = name + "password"
        self.messenger = DirectMessenger("168.235.86.101", self._current_profile.username,self._current_profile.password)
        #ensures valid username is created
        try:
           if not self.messenger.log_in():
             self.error_win("Username is invalid")
             return
        except DsuClientError as ex:
          self.error_win(str(ex))
        else:
          self._current_profile.save_profile(self.profile_filename)
    
    def open_profile(self):
        """
        Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
        data into the UI.
        """
        filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])
        #doesn't throw a console error if the user cancels out of the file exception
        try:
          self.profile_filename = filename.name
        except AttributeError:
          return

        self.body.reset_ui()
        self._current_profile = Profile()
        self._current_profile.load_profile(filename.name)
        self.messenger = DirectMessenger("168.235.86.101", self._current_profile.username,self._current_profile.password)
        try: new_msgs = self.messenger.retrieve_new()
        except DsuClientError as ex:
          self.error_win(str(ex))
          return

        for message in new_msgs:
            if message.sender not in self._current_profile.senders.keys():
              thing1 = []
              thing2 = [DirectMessage("Server","INITIALIZATION MSG",time.time(),self._current_profile.username)] #initialization message to prevent object copying problems
              sndr = Sender(message.sender,thing1,thing2)
              self._current_profile.senders[message.sender] = sndr
            self._current_profile.senders[message.sender].add_message(message)
        
        for sender in self._current_profile.senders.values():
          self.body.insert_sender(sender)
        self._current_profile.save_profile(filename.name)

    
    def close(self):
        """                
        Closes the program when the 'Close' menu item is clicked.
        """
        self.root.destroy()

    def send_message(self):
        """
        Attempts to send the message in the message box to the selected user
        """
        if self.footer.get_entry() != "":
          try:
            sender  = self.body._senders[self.body.current_index]
          except AttributeError:
            self.error_win("Select a sender first, and make sure you have a file open")
            return
          
          try:
            sender  = self.body._senders[self.body.current_index]
            self.messenger.send(self.footer.get_entry(), sender.name)
            self._current_profile.senders[sender.name].add_sent(DirectMessage(sender.name,self.footer.get_entry(),time.time(),self._current_profile.username))
            self.body.set_text_entry(f'{self.body.get_text_entry()}\n{self._current_profile.username}: {self.footer.get_entry()}')
            self.footer.set_entry("")
            self._current_profile.save_profile(self.profile_filename)
          except DsuClientError as ex:
            self.error_win(str(ex))

        
    def add_sender(self):
      '''
      Adds a sender to the profile, by prompting the user for a username
      '''
      usern = simpledialog.askstring("Add sender", "Please enter username")
      try:
        self._current_profile.save_profile(self.profile_filename)
      except AttributeError:
        self.error_win("please open a valid dsu file to use this function.")
        return
      try:
        if usern == self._current_profile.username:
          self.error_win("you can't message yourself!")
          return
        if usern not in self._current_profile.senders.keys():
          thing1 = []
          thing2 = [DirectMessage("Server","PLACEHOLDER MESSAGE TO PREVENT OBJECT REFERENCE PROBLEMS",time.time(),self._current_profile.username)] #PLACEHOLDER MESSAGE TO PREVENT OBJECT REFERENCE PROBLEMS
          self._current_profile.senders[usern] = Sender(usern,thing1,thing2)
          self.body.insert_sender(Sender(usern,thing1,thing2))
        self._current_profile.save_profile(self.profile_filename)
      except TypeError: pass #catches the error instance in which user cancels user selection
    
    def _draw(self):
        """
        Call only once, upon initialization to add widgets to root frame
        """
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.open_profile)
        menu_file.add_command(label='Close', command=self.close)
        menu_file.add_command(label='Stats', command=self.stat_win)

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        self.footer = Footer(self.root, save_callback=self.send_message, sender_callback= self.add_sender)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)
    
    def check(self):
      '''
      Function to continually check for new messages, and update all of the recipients' messages if there are new ones
      In addition, saves the messages history every time it is called
      '''
      try:
        new_msgs = self.messenger.retrieve_new()
      except AttributeError: pass #cathces error that happens when the check is called but no file is opened 
      else:
        if len(new_msgs) != None:
          for message in new_msgs:
            if message.sender not in self._current_profile.senders.keys():
              thing1 = []
              thing2 = [DirectMessage("Server","Start of history",time.time(),self._current_profile.username)] #placeholder to avoid two lsit objects with the same reference
              sndr = Sender(message.sender,thing1,thing2)
              self._current_profile.senders[message.sender] = sndr
              self.body.insert_sender(sndr)
            self._current_profile.senders[message.sender].add_message(message)

            #Refreshes the current selected recipient so that if new messages are sent it can show client in real time
            try:
              current_index = int(self.body.senders_tree.selection()[0])
              sender  = self.body._senders[current_index]
              if sender.name == message.sender:
                self.body.process_messages(sender)
            except IndexError:
              pass #just in case user doesn't have a recipient selected on the node tree
      
      #ensures this process is repeated every second
      main.after(1000,self.check)

if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Chatting service")

    # This is just an arbitrary starting point. You can change the value around to see how
    # the starting size of the window changes. I just thought this looked good for our UI.
    main.geometry("720x580")

    # adding this option removes some legacy behavior with menus that modern OSes don't support. 
    # If you're curious, feel free to comment out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the widgets used in the program.
    # All of the classes that we use, subclass Tk.Frame, since our root frame is main, we initialize 
    # the class with it.
    mapp = MainApp(main)

    # When update is called, we finalize the states of all widgets that have been configured within the root frame.
    # Here, Update ensures that we get an accurate width and height reading based on the types of widgets
    # we have used.
    # minsize prevents the root window from resizing too small. Feel free to comment it out and see how
    # the resizing behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    # And finally, start up the event loop for the program (more on this in lecture).
    #and starts up the continual checking loop
    main.after(1000, mapp.check)
    main.mainloop()