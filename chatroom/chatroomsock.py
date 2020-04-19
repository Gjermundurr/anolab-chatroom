import socket
import threading
import pickle
import pymysql
import bcrypt
from Crypto.Cipher import AES
import os

class ServerSock:
    """ Modified socket operations for backend server

    Includes methods for operations between chat room clients and database interactions.

    """

    def __init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.CONN_LIMIT = 5
        self.IS_ONLINE = {}
        self.s = {}
        self.database_sock = pymysql.connect('localhost', 'server-admin', 'password123', 'Chatroom')

    def accept_sock(self):
        while True:
            client_sock, client_address = self.sock.accept()
            self.clients[client_sock] = client_address
            print('connected: ', client_address)
            threading.Thread(target=self.handle, args=(client_sock,), daemon=True).start()

    def handle(self, sock):
        # Filters the header of each recieved message and runs the
        while True:
            raw_data = sock.recv(1024)
            data = pickle.loads(raw_data)
            while True:
                if not data:
                    break

                elif data['head'] == 'login':
                    self.authenticate_client(sock, data)

                elif data['head'] == 'bcast':
                    self.broadcast(sock, data)

                elif data['head'] == 'dm':
                    pass
            print('Client disconnected: ', self.clients[sock])            
            del self.clients[sock]
            self.IS_ONLINE[sock] = False
            break

    def broadcast(self, sock, data):
        # Additional security token: if user is has not been authorized, token will be False.
        if self.IS_ONLINE[sock]:
            msg = pickle.dumps(data)
            for clients in self.clients:
                if clients != sock:
                    clients.sendall(msg)

    def direct_message(self, source_sock, destination_sock, data):
        pass


    def authenticate_client(self, sock, data):
        auth_username = data['body'][0]
        auth_password = data['body'][1].decode('utf-8')

        cursor = self.database_sock.cursor()
        query = "SELECT username, password FROM clients where username=%s"
        values = (auth_username,)
        cursor.execute(query, values)
        retrieve = cursor.fetchone()
        try:
            if retrieve[0] == auth_username and retrieve[1] == auth_password:
                self.IS_ONLINE[sock] = True
                self.clients[sock] = auth_username
                sock.sendall(bytes('authorized', 'utf-8'))
        except TypeError:
            sock.close()

    def run(self, HOST, PORT):
        """ Executes the socket and starts listening and accepting connections, craetiong a new thread for each client
        """
        self.sock.bind((HOST, PORT))
        self.sock.listen(self.CONN_LIMIT)
        print('Server listening ...')
        while True:
            self.accept_sock()


class ClientSock:
    """ Client socket operations

    """
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.server_address = ('127.0.0.1', 60000)

    def connect(self):
        """ Re-establish the socket object and connect to server """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

    def close(self):
        self.sock.close()

    def auth_credentials(self, username, password):
        """ Hash (password + salt) and send credentials to server for authentication """

        # salt = bcrypt.gensalt()
        salt = '$2b$12$5j4Ce8SPnwfM9FIOtV99C.'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
        credentials = {'head': 'login', 'body': (username, hashed_password)}
        data = pickle.dumps(credentials)
        self.sock.sendall(data)

        data = self.sock.recv(1024)
        if data.decode('utf-8') == 'authorized':
            return True
        else:
            self.sock.close()

    def handle(self):
        """ threaded: will loop for broadcasted messages """
        raw_data = self.sock.recv(1024)
        data = pickle.loads(raw_data)
        return data['body']

    def send(self, message):
        """ """
        raw_data = {'head':'broadcast', 'body': message}
        data = pickle.dumps(raw_data)
        self.sock.sendall(data)


class AESCipher:

    def __init__(self):
        self.key = os.urandom(32)      # AES key
        self.counter = os.urandom(16)  # CTR counter string with length of 16 bytes
        self.enc = AES.new(self.key, AES.MODE_CTR)
        
    def encrypt(self, raw):
        return self.enc.encrypt(raw)
              
    def decrypt(self, raw,):
        return self.decrypt(raw)




cipher = AESCipher()
msg = 'this is clear text.'

crypt_msg = cipher.encrypt(msg)
print(crypt_msg)
clear = cipher.decrypt(crypt_msg)

print(clear)
