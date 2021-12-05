
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



from os import error
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, Label
from tkinter.constants import N
from Profile import Post, Profile, Sender
import time
from ds_client import send
from ds_messenger import DirectMessenger, DirectMessage


class Body(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the body portion of the root frame.
    """
    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # a list of the user objects available in the active DSU file
        self._users = []
        
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Body instance 
        self._draw()
    
    def node_select(self, event):
        """
        Update the entry_editor with the full post entry when the corresponding node in the users_tree
        is selected.
        """
        print(self.users_tree.selection())
        self.current_index = int(self.users_tree.selection()[0])
        user  = self._users[self.current_index]
        self.process_messages(user)
        # print(user.messages)
        # print(user.sent)

        # for message in user.messages:
        #   entry += f'{user.name}: {message.message}\n'
        # for message in user.sent:
        #   entry += f'{message.sender}: {message.message}\n'
        # self.set_text_entry(entry)
    
    def process_messages(self, user: Sender):
      self.set_text_entry(" ")
      entry = ""
      idx1 = 0
      idx2 = 0
      while idx1 < len(user.messages) and idx2 < len(user.sent):
        if float(user.messages[idx1].timestamp) < float(user.sent[idx2].timestamp):
          entry += f'{user.name}: {user.messages[idx1].message}\n'
          idx1 += 1
        else: 
          entry += f'{user.sent[idx2].sender}: {user.sent[idx2].message}\n'
          idx2 += 1
      
      if idx1 == len(user.messages):
        for x in range(idx2,len(user.sent)):
          entry += f'{user.sent[x].sender}: {user.sent[x].message}\n'
      else:
        for x in range(idx1,len(user.messages)):
          entry += f'{user.name}: {user.messages[x].message}\n'
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
    
    def set_users(self, users:list):
        """
        Populates the self._users attribute with posts from the active DSU file.
        """
        for user in users:
            self._users = []
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            self.insert_user(user)
            
    def insert_user(self, user: Sender):
        """
        Inserts a single post to the post_tree widget.
        """
        self._users.append(user)
        id = len(self._users) - 1 #adjust id for 0-base of treeview widget
        self._insert_user_tree(id, user.name)

    def reset_ui(self):
        """
        Resets all UI widgets to their default state. Useful for when clearing the UI is neccessary such
        as when a new DSU file is loaded, for example.
        """
        self.set_text_entry("")
        self.entry_editor.configure(state=tk.NORMAL)
        self._users = []
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

    def _insert_user_tree(self, id, user):
        """
        Inserts a user entry into the users_tree widget.
        """
        #if username is too long, then cuti f off
        if len(user) > 25:
            user = user[:24] + "..."
        
        self.users_tree.insert('', id, id, text=user)
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.users_tree = ttk.Treeview(posts_frame)
        self.users_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.users_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=0)

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
    def __init__(self, root, save_callback=None, user_callback = None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._save_callback = save_callback
        self._user_callback = user_callback
        # IntVar is a variable class that provides access to special variables
        # for Tkinter widgets. is_online is used to hold the state of the chk_button widget.
        # The value assigned to is_online when the chk_button widget is changed by the user
        # can be retrieved using he get() function:
        # chk_value = self.is_online.get()
        self.is_online = tk.IntVar()
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Footer instance 
        self._draw()
    
    def user_click(self):
        """
        Calls the callback function specified in the user class attribute, if
        available, when the add user button has been clicked.
        """
        if self._user_callback is not None:
            self._user_callback()

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

        user_button = tk.Button(master=self, text = "Add User", width = 12, height= 20)
        user_button.configure(command= self.user_click)
        user_button.pack(fill=tk.BOTH, side=tk.TOP, padx =5, pady=50)

        # self.chk_button = tk.Checkbutton(master=self, text="Online", variable=self.is_online)
        # self.chk_button.configure(command=self.online_click) 
        # self.chk_button.pack(fill=tk.BOTH, side=tk.RIGHT)

        # self.footer_label = tk.Label(master=self, text="Ready.")
        # self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)

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

        # Initialize a new NaClProfile and assign it to a class attribute.
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

        self.error_text = tk.Label(win, text=error)
        self.error_text.pack(fill=tk.BOTH, side=tk.TOP)
    
    def new_profile(self):
        """
        Creates a new DSU file when the 'New' menu item is clicked.
        """
        filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')],defaultextension=".dsu")
        self.profile_filename = filename.name

        # TODO Write code to perform whatever operations are necessary to prepare the UI for
        # a new DSU file.
        # HINT: You will probably need to do things like generate encryption keys and reset the ui.
        self.body.reset_ui()
        self._current_profile = Profile()
        name = self.profile_filename[self.profile_filename.rfind("/")+1:-4]
        self._current_profile.username = name
        self._current_profile.password = name + "password"
        self.messenger = DirectMessenger("168.235.86.101", self._current_profile.username,self._current_profile.password)
        self._current_profile.save_profile(self.profile_filename)
    
    def open_profile(self):
        """
        Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
        data into the UI.
        """
        filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])
        self.profile_filename = filename.name

        self.body.reset_ui()
        self._current_profile = Profile()
        self._current_profile.load_profile(filename.name)
        self.messenger = DirectMessenger("168.235.86.101", self._current_profile.username,self._current_profile.password)
        print(self._current_profile.senders)
        for message in self.messenger.retrieve_new():
            if message.sender not in self._current_profile.senders.keys():
              thing1 = []
              thing2 = [DirectMessage("Server","Start of history",time.time(),self._current_profile.username)]
              sndr = Sender(message.sender,thing1,thing2)
              self._current_profile.senders[message.sender] = sndr
            self._current_profile.senders[message.sender].add_message(message)
        
        for sender in self._current_profile.senders.values():
          self.body.insert_user(sender)
        self._current_profile.save_profile(filename.name)

    
    def close(self):
        """                
        Closes the program when the 'Close' menu item is clicked.
        """
        self.root.destroy()

    def send_message(self):
        """
        Sends a message to the server
        """
        if self.footer.get_entry() != "":
          # user  = self.body._users[self.body.current_index]
          try:
            user  = self.body._users[self.body.current_index]
          except:
            self.error_win("some error occured")
          else:
            user  = self.body._users[self.body.current_index]
            self.messenger.send(self.footer.get_entry(), user.name)
            self._current_profile.senders[user.name].add_sent(DirectMessage(user.name,self.footer.get_entry(),time.time(),self._current_profile.username))
            for mess in self._current_profile.senders[user.name].sent:
              print("MESSAGE",mess)
            self.body.set_text_entry(f'{self.body.get_text_entry()}\n{self._current_profile.username}: {self.footer.get_entry()}')
            self.footer.set_entry("")
            self._current_profile.save_profile(self.profile_filename)

        
    def add_user(self):
      '''
      Adds a user to the profile, by prompting the user for a username
      '''
      usern = simpledialog.askstring("Add user", "Please enter username")
      if usern == self._current_profile.username:
        self.error_win("you can't message yourself silly!")
        return
      if usern not in self._current_profile.senders.keys():
        thing1 = []
        thing2 = [DirectMessage("Server","Start of history",time.time(),self._current_profile.username)]
        self._current_profile.senders[usern] = Sender(usern,thing1,thing2)
        self.body.insert_user(Sender(usern,thing1,thing2))
      self._current_profile.save_profile(self.profile_filename)
    
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
        # NOTE: Additional menu items can be added by following the conventions here.
        # The only top level menu item is a 'cascading menu', that presents a small menu of
        # command items when clicked. But there are others. A single button or checkbox, for example,
        # could also be added to the menu bar. 

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        # TODO: Add a callback for detecting changes to the online checkbox widget in the Footer class. Follow
        # the conventions established by the existing save_callback parameter.
        # HINT: There may already be a class method that serves as a good callback function!
        self.footer = Footer(self.root, save_callback=self.send_message, user_callback= self.add_user)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)
    
    def check(self):
      '''
      Function to continually check for messages
      '''
      try:
        new_msgs = self.messenger.retrieve_new()
      except: pass
      else:
        if len(new_msgs) != None:
          for message in new_msgs:
            if message.sender not in self._current_profile.senders.keys():
              thing1 = []
              thing2 = [DirectMessage("Server","Start of history",time.time(),self._current_profile.username)]
              sndr = Sender(message.sender,thing1,thing2)
              self._current_profile.senders[message.sender] = sndr
              self.body.insert_user(sndr)
            self._current_profile.senders[message.sender].add_message(message)

          current_index = int(self.body.users_tree.selection()[0])
          user  = self.body._users[current_index]
          print(user)

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
    main.after(1000, mapp.check)
    main.mainloop()