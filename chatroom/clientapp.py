"""
Classes for tkinter Graphical User Interface configurations, layout, and GUI operations.
"""
import tkinter as tk
from chatroom.clientsock import ClientSock
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
        self.user = None
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
        username = self.username_entry.get()
        password = self.password_entry.get()
        retrieve = client_sock.login(username, password)
        if retrieve['body'][0]:
            root.switch_frame(MainWindow)
            root.user = retrieve['body'][1]
        else:
            messagebox.showwarning('Warning', 'Incorrect username/password!')


class MainWindow(tk.Frame):
    """ Main window of client application
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('XYZ Messenger - Chat room')
        master.protocol('WM_DELETE_WINDOW', self.on_closing)
        threading.Thread(target=self.handler, args=(), daemon=True).start()
        threading.Thread(target=self.is_online, args=(data), daemon=True).start()

        # Top frame containing a right/left frame with the chat window and online users display
        self.top_frame = tk.Frame(self, bg='grey')
        self.left_frame = tk.Frame(self.top_frame, bg='grey')
        self.chat = tk.Text(self.left_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.left_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        self.right_frame = tk.Frame(self.top_frame, bg='grey')
        self.users_online = tk.Listbox(self.right_frame)
        self.users_index = []
        self.users_scroll = tk.Scrollbar(self.right_frame, command=self.users_online.yview)
        self.users_online['yscrollcommand'] = self.users_scroll.set

        self.msg_frame = tk.Frame(self, height=50, padx=5, pady=5, bg='grey')
        self.msg_field = tk.Text(self.msg_frame, height=2, width=10)
        self.msg_btn = tk.Button(self.msg_frame, text='Send', height=2, font='fixedsys 10', command=self.message)
        self.msg_btn.bind('<Return>', self.message)

        # Tkinter widget placements
        self.top_frame.pack(side='top', expand=1, fill='both')
        self.left_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
        self.chat.pack(side='left', expand=1, fill='both')
        self.chat_scroll.pack(side='right', fill='y')

        self.right_frame.pack(side='right', anchor='ne', padx=5, pady=5)
        self.users_online.pack(side='left')
        self.users_scroll.pack(side='right', fill='y')

        self.msg_frame.pack(anchor='sw', side='bottom', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(padx=10, ipadx=20)

    def message(self):
        """ Get input from text widget and send to backend server """

        get = self.msg_field.get('1.0', 'end-1c')
        if len(get) > 0:
            self.chat.config(state='normal')
            self.chat.insert('end', f'You: {get}' + '\n')
            self.chat.config(state='disabled')
            self.msg_field.delete('1.0', 'end')
            message = (root.user, get)
            client_sock.send_msg(message)

    def handler(self):
        while True:
            data = client_sock.receiver()
            if not data:
                break
            if data['head'] == 'bcast':
                message = data['body']
                self.chat.config(state='normal')
                self.chat.insert('end', f'{message[0]}: {message[1]}' + '\n')
                self.chat.config(state='disabled')

            elif data['head'] == 'dm':
                pass

            elif data['head'] == 'meta':
                self.is_online(data['body'])

    def is_online(self, meta):
        ((key, value),) = meta.items()
        if key == 'online':
            self.users_index += [user for user in value]
            for user in value:
                self.users_online.insert('end', user)

        elif key == 'offline':
            for user in self.users_index:
                if value[0] == user:
                    self.users_online.delete(self.users_index.index(user))

    def on_closing(self):
        if messagebox.askokcancel('Exit', 'Exit program?'):
            client_sock.close()
            root.destroy()


class DmWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.top_frame = tk.Frame(self, bg='grey', padx=5, pady=5)
        self.user_label = tk.Label(self.top_frame, text='DM: <User>')
        self.chat_frame = tk.Frame(self.top_frame)
        self.chat = tk.Text(self.chat_frame, width=10, height=1, state='disabled')
        self.chat_scroll = tk.Scrollbar(self.chat_frame, command=self.chat.yview)
        self.chat['yscrollcommand'] = self.chat_scroll.set

        self.btm_frame = tk.Frame(self)
        self.msg_field = tk.Text(self.btm_frame)
        self.msg_btn = tk.Button(self.btm_frame)

        self.top_frame.pack(anchor='sw')
        self.user_label.pack(side='left')
        self.chat_frame.pack(anchor='nw', fill='both', expand=1)
        self.chat.pack(side='left', fill='both', expand=1)
        self.chat_scroll.pack(side='right', fill='y')
        self.btm_frame.pack(anchor='sw', fill='x')
        self.msg_field.pack(side='left', fill='x', expand=1)
        self.msg_btn.pack(side='left')


if __name__ == '__main__':
    client_sock = ClientSock()
    client_sock.start()
    root = Controller()
    root.mainloop()
