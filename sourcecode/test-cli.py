import tkinter as tk
from clientsock import ClientSock
import threading
from tkinter import messagebox
from PIL import ImageTk, Image
from datetime import datetime
import configparser


class Controller(tk.Tk):
    """ The main controller of the tkinter class object derived from tkinters constructor class.
    The Controller class controls the base window of the GUI and includes a method for switching between
    completed "pages" created by the LoginWindow and MainWindow frame classes.
    When instanciated, the parser object reads the contents of a config file for the chat room
    server's IP address and connects to the server, the Diffie-Hellman Key Exchange protocol is then performed
    establishing a shared secret key allowing all further communication to be encrypted.
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.geometry('600x350')
        self.switch_frame(LoginWindow)
        self.configure(bg='grey')
        self.user = None            # the fullname of the logged in user.
        self.dm_instance = {}       # Dictionary containing Toplevel objects with the name of the recipient as key.

        # Create a configparser object and retrieve the IP address written in the config file and
        # instanciate a socket object inputting the server's IP address.
        parser = configparser.ConfigParser()
        parser.read(r'config.txt')
        ip_server = (parser['default']['host'], int(parser['default']['port']))
        self.client_sock = ClientSock(ip_server)
        
        # Attempting to connect to the server; should the server be offline, a message box is
        # displayed and the client application is closed.
        try:
            self.client_sock.start()

        except ConnectionRefusedError:
            messagebox.showerror('Failed to connect.', 'Server is unreachable, please try again later.')
            self.destroy()

    def switch_frame(self, frame_class):
        """Destroy the current page/frame and display a new frame object in the controller window."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='both', expand=1)

    @staticmethod
    def timestamp():
        """Method for returning a HH:MM timestamp for the chat rooms messages."""
        timestamp = datetime.now()
        return f'{timestamp.hour}:{timestamp.minute}'


class LoginWindow(tk.Frame):
    """ Login window: First page of the application.
    Display a welcome page where the user is prompted with a username & password entry field.
    Clicking the Login button sends the user's credentials to the server for authentication.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('XYZ Messenger: Login')
        master.protocol('WM_DELETE_WINDOW', lambda: root.destroy())
        self.configure(bg='grey')

        # The Login page is divided into three parent frames (top_frame, middle_frame, btm_frame).
        # Top frame contains the banner logo.
        self.top_frame = tk.Frame(self)
        self.img = Image.open('../img/xyz_banner.png')
        self.img100x320 = self.img.resize((370, 120), Image.ANTIALIAS)
        self.banner = ImageTk.PhotoImage(self.img100x320)
        self.logo_label = tk.Label(self.top_frame, height=150, width=400, image=self.banner, bg='grey')

        # Middle frame contains a welcome message with important information, and the two username & password text labels.
        self.middle_frame = tk.Frame(self, bg='grey', height=150, width=400)
        self.info = tk.Label(self.middle_frame, bg='grey', font='ubuntu 9 bold', text="""Welcome to Company XYZ's personal encrypted messaging service,
    please enter below your username and password sent to you by email.
        
        N.B Do not share this application without permission!
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
        self.login_button.bind('<Return>', self.login)

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
            root.switch_frame(MainWindow)
            root.user = retrieve['body'][1]
        else:
            messagebox.showwarning('Warning', 'Incorrect username/password!')


class MainWindow(tk.Frame):
    """ Client application: Main Window.
    The Main Window gives access to the group chat, allowing the user to receive and send broadcasted messages. 
    The main window includes a large text box for displaying the chat room's messages and a panel on the right-hand
    side containing the names of all connected users with the feature of right-clicking a name to open a private chat window
    for communication between two users.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('XYZ Messenger - Chat room')
        master.protocol('WM_DELETE_WINDOW', self.on_closing)
        threading.Thread(target=self.handler, args=(), daemon=True).start()
        self.online = {}
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
        self.users_frame = tk.Frame(self.right_frame)
        self.users_canvas = tk.Canvas(self.users_frame, width=130, height=190)
        self.users_scrollbar = tk.Scrollbar(self.users_frame, orient='vertical', command=self.users_canvas.yview)
        self.users_scrollframe = tk.Frame(self.users_canvas)
        self.users_scrollframe.bind('<Configure>',
                                    lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox('all')))
        self.users_canvas.create_window((0, 0), window=self.users_scrollframe, anchor='nw')
        self.users_canvas.configure(yscrollcommand=self.users_scrollbar.set)
        self.online_icon = ImageTk.PhotoImage(Image.open('../img/Green-icon-10x10.png'))

        # Msg_frame is the bottom part of the window and contains the entry field and send button.
        self.msg_frame = tk.Frame(self, height=50, padx=5, pady=5, bg='grey')
        self.msg_field = tk.Text(self.msg_frame, height=2, width=10, font='ubuntu 11')
        self.msg_btn = tk.Button(self.msg_frame, text='Send', height=2, font='fixedsys 10', command=self.message)
        self.msg_btn.bind('<Return>', self.message)

        # Placement configurations of all frame objects using the Pack() manager.
        self.top_frame.pack(side='top', expand=1, fill='both')
        self.left_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
        self.chat.pack(side='left', expand=1, fill='both')
        self.chat_scroll.pack(side='right', fill='y')
        self.right_frame.pack(side='right', anchor='ne', padx=5, pady=5)
        self.users_frame.pack()
        self.users_canvas.pack(side='left', fill='both')
        self.users_scrollbar.pack(side='right', fill='y')

        self.msg_frame.pack(anchor='sw', side='bottom', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(padx=10, ipadx=20)

    def message(self, event=None):
        """ Actions performed when clicking Send button.
        Retrieve the message entered in the message field and insert into local chat box, then send the message
        to the server marked as a broadcasted message.
        """

        get = self.msg_field.get('1.0', 'end-1c')
        if len(get) > 0:
            self.chat.config(state='normal')
            self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
            self.chat.insert('end', 'You:', 'name')
            self.chat.insert('end', f' {get}' + '\n', 'message')
            self.chat.config(state='disabled')
            self.chat.see('end')
            self.msg_field.delete('1.0', 'end')
            root.client_sock.send(head='bcast', message=(root.user, get))

    def handler(self):
        """The handler for all receiving communication.
        The handler is a switchboard for performing the correct action based on the information found in the message's
        header-field.
        
        All messages follow a head & body structure for identifying message's destination:
            'bcast' ==  broadcast: This contains a message for the group chat.
            'dm'    ==  direct message: This is a message belonging to a private conversation.
            'meta'  ==  meta data: Used by the online-panel to know who is online or offline.

        Example:    Message = {'head':'bcast', 'body': message}  
                    Message = {'head':'dm', 'body': (destination, message)}  
                    Message = {'head':'meta', 'body': {'online'/'offline': [user1, user2, user3]}}  
        """
        while True:
            # Receive a message from the server
            data = root.client_sock.receiver()
            if not data:
                continue
            
            if data == 'ConnectionError':
                # An exception has occured causing the connection with the server to break.
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
                # Private conversation:
                # Check for an existing Top-level window, if not found, create a new one.
                def check_instance(user):
                    # creating definition to not terminate Handle loop upon returning
                    for dm in root.dm_instance.items():
                        if user['body'][1] in dm:
                            dm[1].display(user['body'])
                            return

                    new_dm = DmWindow(root, data['body'][1])
                    new_dm.display(data['body'])
                    root.dm_instance[data['body'][1]] = new_dm
                check_instance(data)

            elif data['head'] == 'meta':
                # Meta data
                self.is_online(data['body'])

    def is_online(self, meta):
        """ Management of online-users panel.
        creates a label with the name of the user and bind a right-click menu option for creating a private conversation.
        """
        ((key, value),) = meta.items()
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

        elif key == 'offline':
            # Create a temporary object of the 'online' dictionary used by the itterator.
            # Locate the dict value matching the received name, destroy the label
            # and delete the object from the original dictionary.
            online_tmp = self.online.copy()
            for client in online_tmp:
                if client == value:
                    user_lbl = self.online[client]
                    user_lbl.destroy()
                    del self.online[client]

    @staticmethod
    def direct_message(user):
        """ Create a Toplevel window for private conversations.
        Check if an existing Top-level object exists based on the 'user' argument or create a new window if not found.
        """
        for dm in root.dm_instance.items():
            if user in dm:
                dm[1].lift()
                return
        # if the loop does not find an existing DM conversation, a new Toplevel window is created
        new_dm = DmWindow(root, user)
        root.dm_instance[user] = new_dm
        new_dm.lift()

    @staticmethod
    def on_closing():
        """ Function for controller window's top-right exit button.
        """
        if messagebox.askokcancel('Exit', 'Exit application?'):
            root.client_sock.close()
            root.destroy()


class PopupMenu(tk.Menu, MainWindow):
    """ Class for passing a variable through the context-menu to the direct_message method."""
    def __init__(self):
        tk.Menu.__init__(self, tearoff=0)
        self.to_user = None # The name of the other end-point of the private conversation.
        self.add_command(label='Direct Message', command=self.act)

    def act(self):
        self.direct_message(self.to_user)

    def popup(self, x, y, select):
        self.to_user = select
        self.tk_popup(x, y)


class DmWindow(tk.Toplevel):
    """ Creating Toplevel windows for private conversations between two individuals.
    The Toplevel is a separate window from the main client application and includes a small chat box
    and entry field for private conversations.
    """
    def __init__(self, master, to_user):
        tk.Toplevel.__init__(self, master)
        self.to_user = to_user
        self.title(f'Private Message: {self.to_user}')
        self.geometry('300x220')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.configure(bg='grey')
        self.chat_frame = tk.Frame(self, padx=5, pady=5, bg='grey')
        self.chat = tk.Text(self.chat_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.chat_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        self.chat.tag_config('sysmessage', foreground='lightgrey', font='ubuntu 9 bold')
        self.chat.tag_config('timestamp', foreground='steelblue', font='fixedsys 12')
        self.chat.tag_config('message', foreground='black', font='ubuntu 11')
        self.chat.tag_config('name', foreground='black', font='ubuntu 10 bold')

        self.chat.configure(state='normal')
        self.chat.insert('end', ' ' * 15 + '(This is a private conversation)' + '\n', 'sysmessage')
        self.chat.configure(state='disabled')

        self.btm_frame = tk.Frame(self, padx=5, pady=5, bg='grey')
        self.msg_field = tk.Text(self.btm_frame, width=10, height=2, font='ubuntu 11')
        self.msg_btn = tk.Button(self.btm_frame, padx=5, text='Send', height=2, font='fixedsys 10',
                                 command=self.message)

        # Positioning
        self.chat_frame.pack(anchor='nw', fill='both', expand=1)
        self.chat.pack(side='left', fill='both', expand=1)
        self.chat_scroll.pack(side='right', fill='y')

        self.btm_frame.pack(anchor='sw', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(side='left')

    def display(self, data):
        self.chat.config(state='normal')
        self.chat.insert('end', f'{root.timestamp()} ', 'timestamp')
        self.chat.insert('end', f'{data[1]}:', 'name')
        self.chat.insert('end', f' {data[2]}' + '\n', 'message')
        self.chat.config(state='disabled')
        self.chat.see('end')

    def message(self):
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
        self.destroy()
        del root.dm_instance[self.to_user]


if __name__ == '__main__':
    root = Controller()
    root.mainloop()
