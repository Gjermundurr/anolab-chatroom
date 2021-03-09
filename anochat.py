import tkinter as tk
from modules.clientsock import ClientSock
import threading
from tkinter import messagebox
from PIL import ImageTk, Image
from datetime import datetime


class Controller(tk.Tk):
    """ The main controller of the tkinter class object derived from tkinters constructor class.
        The Controller class controls the base window of the GUI and includes a method for switching between
        completed "pages" created by the LoginPage and MainPage frame classes.
        When instanciated, the parser object reads the contents of a config file for the chat room
        server's IP address and connects to the server, the Diffie-Hellman Key Exchange protocol is then performed
        establishing a shared secret key allowing all further communication to be encrypted.
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.geometry('600x350')
        self.iconbitmap('img/client-icon-trans.ico')    # Set window icon 
        self.server_address = ('188.166.75.232',42066)
        self.switch_frame(LoginPage)  # Bind LoginPage to window object
        self.user = None                # the fullname of the logged in user.
        self.dm_instance = {}           # Dictionary containing Toplevel objects with the name of the recipient as key
        self.client_sock = ClientSock(self.server_address)
        self.statusinfo = tk.StringVar()
        self.statusbar = tk.Label(self, textvariable=self.statusinfo, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)


    def connect_to_server(self):
        try:
            self.client_sock.start()
            self.statusbar.config(bg='lightgreen')
            self.statusinfo.set(f'Server: {self.server_address[0]} Port: {self.server_address[1]} Status: Connected')
            
        except ConnectionRefusedError:
            messagebox.showerror('Failed to connect.', 'Server is unreachable, please try again later.')
            self.statusbar.config(bg='tomato3')
            self.statusinfo.set(f'Server: {self.server_address[0]} Port: {self.server_address[1]} Status: Disconnected')
    
            

        

    def switch_frame(self, frame_class):
        """ Destroy the current page/frame and bind a new frame object in the controller window.
        """
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='both', expand=1)

    @staticmethod
    def timestamp():
        """ Method for returning a HH:MM timestamp displayed together with the chat room's messages.
        """
        timestamp = datetime.now()
        return f'{timestamp.hour}:{timestamp.minute}'






class LoginPage(tk.Frame):
    """ Login window: First page of the application.
    When the Login page is reached, the Diffie-Hellman Key Exchange is finished and all data thereafter
    will be encrypted. A welcome page is displayed to the user with a banner image and two entry fields
    requesting a username & password. Clicking the Login button sends the user's credentials to the server
    for authentication. Based on the outcome of the authentication, the user will either be displayed an
    error message or enter the Main page of the application.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('AnoLab06: Login')
        master.protocol('WM_DELETE_WINDOW', lambda: root.destroy())
        self.configure(bg='grey')
        
        # The Login page is divided into three parent frames (top_frame, middle_frame, btm_frame).
        # Top frame contains the banner logo.
        self.top_frame = tk.Frame(self)
        self.img = Image.open('img/login-banner.png')
        self.img100x320 = self.img.resize((370, 120), Image.ANTIALIAS)
        self.banner = ImageTk.PhotoImage(self.img100x320)
        self.logo_label = tk.Label(self.top_frame, height=150, width=400, image=self.banner, bg='grey')

        # Middle frame contains a welcome message with important information, and the two username & password text labels.
        self.middle_frame = tk.Frame(self, bg='grey', height=150, width=400)
        self.info = tk.Label(self.middle_frame, bg='grey', font='ubuntu 9 bold', text="""Welcome to Anolab06's encrypted chatroom.
    Enter below your username and password.
        """)
        self.username_label = tk.Label(self.middle_frame, text='Username:', font='ubuntu 10 bold', bg='grey',
                                       fg='white')
        self.password_label = tk.Label(self.middle_frame, text='Password:', font='ubuntu 10 bold', bg='grey',
                                       fg='white')

        # Bottom frame contains the entry fields and login button stacked next to eachother from left to right.
        self.btm_frame = tk.Frame(self, height=150, width=400, bg='grey')
        self.username_entry = tk.Entry(self.btm_frame, font='fixedsys 10')
        self.password_entry = tk.Entry(self.btm_frame, show='*')
        self.login_button = tk.Button(self.btm_frame, text='Login', font='fixedsys 10', command=self.login)
        master.bind('<Return>', self.login)
        

        # Placement configurations of all frame objects using the Pack() manager.
        self.top_frame.pack()
        self.logo_label.pack()
        self.middle_frame.pack()
        self.info.pack(ipady=10)
        self.username_label.pack(side='left', padx=60)
        self.password_label.pack(side='left', padx=40)
        self.btm_frame.pack()
        self.username_entry.pack(side='left', padx=10)
        self.password_entry.pack(side='left', padx=10)
        self.login_button.pack(side='left')


    def login(self, event=None):
        """ Actions performed when clicking the Login button.
            The credentials are encrypted and sent to the server for authorization, the server will reply
            with a message containing a True or False boolean value indicating the outcome of the authentication process.
            Should the authentication be successfull, the user's real name is also included in the reply message
            and stored as a variable in the Controller class.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()
        retrieve = root.client_sock.login(username, password)
        if retrieve['body'][0]:
            root.switch_frame(MainPage)
            root.user = retrieve['body'][1]
        else:
            messagebox.showwarning('Warning', 'Incorrect username/password!')


class MainPage(tk.Frame):
    """ Client application: Main Page.
        The Main Window gives access to the group chat, allowing the user to receive and send broadcasted messages. 
        The main window includes a large text box for displaying the chat room's messages and a panel on the right-hand
        side containing the names of all connected users with the feature of right-clicking a name to open a private chat window
        for communication between two users.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('AnoLab06: Chatroom')
        master.protocol('WM_DELETE_WINDOW', self.on_closing)
        threading.Thread(target=self.handler, args=(), daemon=True).start()
        self.online = {}            # container for referencing online-user labels, ex: 'NameOfUser': Label.user)
        self.menu = PopupMenu()

        # The Main Window is divided into a parent top and bottom frame.
        # The Top frame is further split into a left-frame containing the chat box
        # and a right-frame containing the online-users panel.
        self.top_frame = tk.Frame(self, bg='grey')
        self.left_frame = tk.Frame(self.top_frame, bg='grey')
        self.chat = tk.Text(self.left_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.left_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        # Specific design configurations for different parts of the displayed messages.
        self.chat.tag_config('timestamp', foreground='steelblue', font='fixedsys 12')
        self.chat.tag_config('message', foreground='black', font='ubuntu 11')
        self.chat.tag_config('name', foreground='black', font='ubuntu 10 bold')

        # Right-frame widgets
        self.right_frame = tk.Frame(self.top_frame, bg='grey')
        self.info_label = tk.Label(self.right_frame, text='Online users:')
        self.users_frame = tk.Frame(self.right_frame)
        self.users_canvas = tk.Canvas(self.users_frame, width=130, height=190)
        self.users_scrollbar = tk.Scrollbar(self.users_frame, orient='vertical', command=self.users_canvas.yview)
        self.users_scrollframe = tk.Frame(self.users_canvas)
        self.users_scrollframe.bind('<Configure>',
                                    lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox('all')))
        self.users_canvas.create_window((0, 0), window=self.users_scrollframe, anchor='nw')
        self.users_canvas.configure(yscrollcommand=self.users_scrollbar.set)
        self.online_icon = ImageTk.PhotoImage(Image.open('img/Green-icon-10x10.png'))

        # Msg_frame is the bottom part of the window and contains the entry field and send button.
        self.msg_frame = tk.Frame(self, height=50, padx=5, pady=5, bg='grey')
        self.msg_field = tk.Text(self.msg_frame, height=2, width=10, font='ubuntu 11')
        self.msg_btn = tk.Button(self.msg_frame, text='Send', height=2, font='fixedsys 10', command=self.message)
        master.bind('<Return>', self.message)

        # Placement configurations of all frame objects using the Pack() manager.
        self.top_frame.pack(side='top', expand=1, fill='both')
        self.left_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
        self.chat.pack(side='left', expand=1, fill='both')
        self.chat_scroll.pack(side='right', fill='y')
        self.right_frame.pack(side='right', anchor='ne', padx=5, pady=5)
        self.info_label.pack(fill='x')
        self.users_frame.pack()
        
        self.users_canvas.pack(side='left', fill='both')
        self.users_scrollbar.pack(side='right', fill='y')

        self.msg_frame.pack(anchor='sw', side='bottom', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(padx=10, ipadx=20)

    def message(self, event=None):
        """ Actions performed when clicking the Send button. Retrieve the message entered in the message field
            and insert into local chat box, then send the message to the server marked as a broadcasted message.
        """

        get = self.msg_field.get('1.0', 'end-1c')
        if len(get) > 0:
            self.chat.config(state='normal')
            self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
            self.chat.insert('end', 'You:', 'name')
            self.chat.insert('end', f' {get}', 'message') #  removed: + '\n'
            self.chat.config(state='disabled')
            self.chat.see('end')
            self.msg_field.delete('1.0', 'end')
            root.client_sock.send(head='bcast', message=(root.user, get))

    def handler(self):
        """The handler for all receiving communication.
            The handler is a switchboard for performing the correct action based on the information found in the message's
            header-field. All messages follow a head & body structure for identifying message's destination:
                
            'bcast' ==  broadcast: This contains a message for the group chat.
            'dm'    ==  direct message: This is a message belonging to a private conversation.
            'meta'  ==  meta data: Used by the online-panel to know who is online or offline.

            Example:    Message = {'head':'bcast', 'body': message}  
                        Message = {'head':'dm', 'body': (source, destination, message)}  
                        Message = {'head':'meta', 'body': {'online'/'offline': [user1, user2, user3]}}  
        """
        while True:
            # Receive a message from the server
            data = root.client_sock.receiver()
            
            if not data:
                continue
            
            elif data == 'ConnectionError':
                # An exception has occured causing the connection with the server to break.
                root.statusbar.config(bg='tomato3')
                root.statusinfo.set(f'Server: {self.server_address[0]} Port: {self.server_address[1]} Status: Disconnected')
                messagebox.showerror('Lost connection to server!', 'You have been disconnected from the chat room, please restart your application.')
                break

            elif data['head'] == 'bcast':
                # Broadcasted message.
                message = data['body']
                self.chat.config(state='normal')
                self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
                self.chat.insert('end', f'{message[0]}:', 'name')
                self.chat.insert('end', f' {message[1]}' + '\n', 'message')
                self.chat.config(state='disabled')
                self.chat.see('end')

            elif data['head'] == 'dm':
                # Check for an existing conversation in the dm_instance container, else create one.
                def check_instance(user):
                    # creating definition to not terminate Handle loop upon returning
                    for dm in root.dm_instance.items():
                        if user['body'][1] in dm:
                            dm[1].display(user['body'])         # Insert message in existing conversation
                            return                              # Return to loop

                    # No existing conversation was found; a conversation is created.
                    new_dm = DmWindow(root, data['body'][1])    # Create new Toplevel window
                    new_dm.display(data['body'])                # insert message in chat box
                    root.dm_instance[data['body'][1]] = new_dm  # save a reference of the object
                check_instance(data)

            elif data['head'] == 'meta':
                # Meta data
                self.is_online(data['body'])

    def is_online(self, meta):
        """ Management of the online-users panel. The method receives messages with the 'meta' header and contain the names of other users
            either going online or offline. The online-users panel contains tkinter Label objects displaying the name of another user in the chat room.
            The labels are configured to change color when the mouse enters and leaves its hitbox, indicating that the element is 'alive'. Each label
            is right-clickable which opens a small context-menu giving the option of sending a direct message to a spesific user. 
        """

        ((key, value),) = meta.items()
        # creates a new label for each name recieved:
        if key == 'online':
            for client in value:
                def make_lambda(name):
                    return lambda e: self.menu.popup(e.x_root, e.y_root, name)

                if client != root.user:
                    user_lbl = tk.Label(self.users_scrollframe, text=f' {client}', image=self.online_icon, compound='left')
                    user_lbl.pack(anchor='w')
                    user_lbl.bind('<Enter>', lambda event, h=user_lbl: h.configure(bg='lightblue')) # Cause the label to highlight when moused over.
                    user_lbl.bind('<Leave>', lambda event, h=user_lbl: h.configure(bg='#F0F0F0'))   # Return to original color as mouse leaves the label.
                    user_lbl.bind('<Button-3>', make_lambda(client))                                # Bind right-click to context menu.
                    self.online[client] = user_lbl                                                  # Add reference to dictionary.

        # delete the label matching the received name:
        # Create a copy of the 'online' dictionary used by the itterator.
        # Locate the dict value matching the received name, destroy the label
        # and delete the object from the original dictionary.
        elif key == 'offline':
            online_tmp = self.online.copy()
            for client in online_tmp:
                if client == value:
                    user_lbl = self.online[client]
                    user_lbl.destroy()          # destroy Label object
                    del self.online[client]     # delete reference

    @staticmethod
    def on_closing():
        """ Display a message to the user asking if he wants to exit the application.
            Method bound to the Controller windows red exit button in top-right corner.
            Sends a TCP FIN flag to server indicating that the socket can be closed, and destroy the client application.
        """
        if messagebox.askokcancel('Exit', 'Exit application?'):
            root.client_sock.close()        # send socket.shutdown(1) to server
            root.destroy()                  # Destroy entire client application

    @staticmethod
    def direct_message(user):
        """ Create a Toplevel window for private conversations using the DmWindow class. The method first checks for an
            existing Top-level window matching the 'user' argument, if not, a new DmWindow object is created.
        """
        # Search for existing conversation:
        for dm in root.dm_instance.items():
            if user in dm:
                dm[1].lift()                # Lift window to foreground.
                return
        
        # No conversation was found:
        new_dm = DmWindow(root, user)       # Create Toplevel window.
        root.dm_instance[user] = new_dm     # Save reference.
        new_dm.lift()                       # Lift to foreground.


class PopupMenu(tk.Menu, MainPage):
    """ Class for passing a variable through the context-menu to the direct_message method.
        The popup method is bound to a custom lambda function on each online-user Label to
        allow the Label's name to be retrieved and passed onwards to the direct_message method.
    """
    def __init__(self):
        tk.Menu.__init__(self, tearoff=0)
        self.to_user = None # The name of the private conversation's recipient.
        self.add_command(label='Direct Message', command=self.act)

    def act(self):
        self.direct_message(self.to_user)

    def popup(self, x, y, select):
        # Grab the name written on the selected Label object and bind to 'self.to_user'
        self.to_user = select
        self.tk_popup(x, y)


class DmWindow(tk.Toplevel):
    """ Creating Toplevel windows for private conversations between two individuals.
        The Toplevel is a separate window from the main client application and is a minimal version of
        the MainPage window.
    """
    def __init__(self, master, to_user):
        tk.Toplevel.__init__(self, master)
        self.to_user = to_user
        self.title(f'Private Message: {self.to_user}')
        self.geometry('300x220')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.configure(bg='grey')
        
        # Top frame containing the chat box
        self.chat_frame = tk.Frame(self, padx=5, pady=5, bg='grey')
        self.chat = tk.Text(self.chat_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.chat_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        # Bottom frame containing the entry field and send button
        self.btm_frame = tk.Frame(self, padx=5, pady=5, bg='grey')
        self.msg_field = tk.Text(self.btm_frame, width=10, height=2, font='ubuntu 11')
        self.msg_btn = tk.Button(self.btm_frame, padx=5, text='Send', height=2, font='fixedsys 10',
                                 command=self.message)
        self.bind('<Return>', self.message)

        # Text-format configurations
        self.chat.tag_config('sysmessage', foreground='lightgrey', font='ubuntu 9 bold')
        self.chat.tag_config('timestamp', foreground='steelblue', font='fixedsys 12')
        self.chat.tag_config('message', foreground='black', font='ubuntu 11')
        self.chat.tag_config('name', foreground='black', font='ubuntu 10 bold')

        # insert informational message at launch
        self.chat.configure(state='normal')
        self.chat.insert('end', ' ' * 15 + '(This is a private conversation)' + '\n', 'sysmessage')
        self.chat.configure(state='disabled')

        # Placement configurations
        self.chat_frame.pack(anchor='nw', fill='both', expand=1)
        self.chat.pack(side='left', fill='both', expand=1)
        self.chat_scroll.pack(side='right', fill='y')
        self.btm_frame.pack(anchor='sw', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(side='left')

        

    def display(self, data):
        # Insert a message to the DmWindow's chat box
        self.chat.config(state='normal')
        self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
        self.chat.insert('end', f'{data[1]}:', 'name')
        self.chat.insert('end', f' {data[2]}' + '\n', 'message')
        self.chat.config(state='disabled')
        self.chat.see('end')

    def message(self, event=None):
        # Send a message 
        get = self.msg_field.get('1.0', 'end-1c')
        if len(get) > 0:
            self.chat.config(state='normal')
            self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
            self.chat.insert('end', 'You:', 'name')
            self.chat.insert('end', f' {get}' + '\n', 'message')
            self.chat.config(state='disabled')
            self.chat.see('end')
            self.msg_field.delete('1.0', 'end')
            root.client_sock.send(head='dm', recipient=self.to_user, sender=root.user, message=get)

    def on_closing(self):
        # Close Dm window
        self.destroy()
        del root.dm_instance[self.to_user]


if __name__ == '__main__':
    root = Controller()
    root.connect_to_server()
    root.mainloop()
