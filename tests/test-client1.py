import tkinter as tk
from chatroom.chatroomsock import ClientSock
import threading


class Controller(tk.Tk):
    """ Constructor for GUI application
    """
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.geometry('600x350')
        self.switch_frame(LoginWindow)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class LoginWindow(tk.Frame):
    """ Login window:

    require user to enter valid authentication

    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('Test: GUI client login')

        # Construction and Configuration of all elements
        self.logo_frame = tk.Frame(self, height='100', width='200', bg='black')
        self.user_frame = tk.Frame(self)
        self.username_label = tk.Label(self.user_frame, text='Username:')
        self.password_label = tk.Label(self.user_frame, text='Password:')
        self.entry_frame = tk.Frame(self)
        self.username_entry = tk.Entry(self.entry_frame)
        self.password_entry = tk.Entry(self.entry_frame, show='*')
        self.login_button = tk.Button(self.entry_frame, text='Login',
                                      command=self.login)

        # Placements of all elements relative to each other
        self.logo_frame.pack(pady=10, ipady=20)
        self.user_frame.pack(pady=10, ipady=20)
        self.username_label.pack(side='left', ipadx=25)
        self.password_label.pack(side='left', padx=25)
        self.entry_frame.pack()
        self.username_entry.pack(side='left', ipadx=5)
        self.password_entry.pack(side='left', padx=5)
        self.login_button.pack(side='left', ipadx=5)

    def login(self):
        client_sock.connect()
        username = self.username_entry.get()
        password = self.password_entry.get()
        value = client_sock.auth_credentials(username, password)
        if value:
            root.switch_frame(MainWindow)


class MainWindow(tk.Frame):
    """ Main window of client application
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('Test: Client App User 2')
        threading.Thread(target=self.broadcast, args=()).start()

        # Construction and Configuration of all elements
        self.first_frame = tk.Frame(self)
        self.display_chat = tk.Text(self.first_frame, height=15, width=55,
                                    state='disabled')
        self.display_users = tk.Listbox(self.first_frame)
        self.second_frame = tk.Frame(self)
        self.msg_field = tk.Text(self.second_frame, height=1, width=55)
        self.msg_button = tk.Button(self.second_frame, text='Enter',
                                    command=self.get_msg)

        # Placements of all elements relative to each other
        self.first_frame.pack(pady=5, ipadx=4)
        self.display_chat.pack(side='left')
        self.display_users.pack(anchor='e')
        self.second_frame.pack(anchor='w')
        self.msg_field.pack(side='left')
        self.msg_button.pack(side='left', padx=10)

    def get_msg(self):
        """ Retreive chatbox and send to socket """

        self.display_chat.config(state='normal')
        message = self.msg_field.get('1.0', 'end-1c')
        self.display_chat.insert('end', message + '\n')
        self.msg_field.delete('1.0', 'end')
        self.display_chat.config(state='disabled')
        client_sock.send(message)
        print(message)

    def broadcast(self):
        while True:
            message = client_sock.handle()
            print(message)
            self.display_chat.config(state='normal')
            self.display_chat.insert('end', message + '\n')
            self.display_chat.config(state='disabled')


if __name__ == '__main__':
    root = Controller()
    client_sock = ClientSock()
    root.mainloop()

