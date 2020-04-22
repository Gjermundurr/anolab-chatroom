import tkinter as tk
from chatroom.chatroomsock import ClientSock
import threading
from tkinter import messagebox
from PIL import ImageTk, Image


class Controller(tk.Tk):
    """ Constructor for GUI application
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.geometry('600x350')
        self.switch_frame(LoginWindow)
        self._user = None
        self.configure(bg='grey')

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='both', expand=1)


class LoginWindow(tk.Frame):
    """ Login window:

    require user to enter valid authentication

    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('XYZ Messenger: Login')
        master.protocol('WM_DELETE_WINDOW', lambda: root.destroy())
        self.configure(bg='grey')

        self.top_frame = tk.Frame(self)
        self.img = Image.open('../img/xyz_banner.png')
        self.img100x320 = self.img.resize((370, 120), Image.ANTIALIAS)
        self.banner = ImageTk.PhotoImage(self.img100x320)
        self.logo_label = tk.Label(self.top_frame, height=150, width=400, image=self.banner, bg='grey')

        self.middle_frame = tk.Frame(self, bg='grey', height=150, width=400)
        self.info = tk.Label(self.middle_frame, bg='grey', font='times 11', text="""Welcome to Company XYZ's personal encrypted messaging service,
        Do not share this application without permission!
        
        Please enter below your username and password sent to you by email.
        """)
        self.username_label = tk.Label(self.middle_frame, text='Username:', font='fixedsys 13', bg='grey',
                                       fg='white')
        self.password_label = tk.Label(self.middle_frame, text='Password:', font='fixedsys 13', bg='grey',
                                       fg='white')

        self.btm_frame = tk.Frame(self, height=150, width=400, bg='grey')
        self.username_entry = tk.Entry(self.btm_frame, font='fixedsys 10')
        self.password_entry = tk.Entry(self.btm_frame, show='*')
        self.login_button = tk.Button(self.btm_frame, text='Login', font='fixedsys 10', command=self.login)

        # widget placement
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

    def login(self):
        client_sock.connect()
        username = self.username_entry.get()
        password = self.password_entry.get()
        value = client_sock.auth_credentials(username, password)
        if value:
            root.switch_frame(MainWindow)
            # root._user = username
            root._user = 'jerry'
        else:
            client_sock.close()


class MainWindow(tk.Frame):
    """ Main window of client application
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        # master.resizable(width=True, height=True)
        master.title('XYZ Messenger - Chat room')
        master.protocol('WM_DELETE_WINDOW', self.on_closing)
        threading.Thread(target=self.broadcast, args=(), daemon=True).start()

        # Top frame containing a right/left frame with the chat window and online users display
        self.top_frame = tk.Frame(self)
        self.left_frame = tk.Frame(self.top_frame)
        self.chat = tk.Text(self.left_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.left_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        self.right_frame = tk.Frame(self.top_frame)
        self.users_online = tk.Listbox(self.right_frame)
        self.users_scroll = tk.Scrollbar(self.right_frame, command=self.users_online.yview)
        self.users_online['yscrollcommand'] = self.users_scroll.set

        self.msg_frame = tk.Frame(self, height=50, padx=5, pady=5)
        self.msg_text = tk.Text(self.msg_frame, height=2, width=10)
        self.msg_btn = tk.Button(self.msg_frame, text='Send', height=2, font='fixedsys 10', command=self.get_message)
        self.msg_btn.bind('<Return>', self.get_message)

        # Tkinter widget placements
        self.top_frame.pack(side='top', expand=1, fill='both')
        self.left_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
        self.chat.pack(side='left', expand=1, fill='both')
        self.chat_scroll.pack(side='right', fill='y')

        self.right_frame.pack(side='right', anchor='ne', padx=5, pady=5)
        self.users_online.pack(side='left')
        self.users_scroll.pack(side='right', fill='y')

        self.msg_frame.pack(anchor='sw', side='bottom', fill='x')
        self.msg_text.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(padx=10, ipadx=20)

    def get_message(self):
        """ Get input from text widget and send to backend server """

        self.chat.config(state='normal')
        get = self.msg_text.get('1.0', 'end-1c')
        self.chat.insert('end', '\n', f'You: {get}')
        self.msg_text.delete('1.0', 'end')
        self.chat.config(state='disabled')
        message = {root._user: get}
        client_sock.send(message)

    def broadcast(self):
        while True:
            message = client_sock.handle()
            self.chat.config(state='normal')
            for k, v in message.items():
                self.chat.insert('end', '\n', f'{k}: {v}')
            self.chat.config(state='disabled')

    def on_closing(self):
        if messagebox.askokcancel('Exit', 'Exit program?'):
            client_sock.close()
            root.destroy()


if __name__ == '__main__':
    root = Controller()
    client_sock = ClientSock()
    root.mainloop()
