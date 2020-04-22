import socket
import threading
import pickle
import pymysql
import bcrypt # remove?
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
# from Crypto.Random import get_random_bytes


class ServerSock:
    """ Modified socket operations for backend server

    Includes methods for operations between chat room clients and database interactions.

    """

    def __init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CONN_LIMIT = 5
        self.clients = {}       # sock: username
        self.IS_ONLINE = {}     # sock: bool
        self.database_sock = pymysql.connect('localhost', 'server-admin', 'password123', 'chatroom_v1')

    def accept_sock(self):
        while True:
            client_sock, client_address = self.sock.accept()
            self.clients[client_sock] = client_address
            print('connected: ', client_address)
            threading.Thread(target=self.handle, args=(client_sock,), daemon=True).start()

    def authenticate_client(self, sock, data):
        auth_username = data['body'][0]
        auth_password = data['body'][1].decode('utf-8')

        cursor = self.database_sock.cursor()
        query = "SELECT username, password FROM users where username=%s"
        values = (auth_username,)
        cursor.execute(query, values)
        retrieve = cursor.fetchone()
        try:
            if retrieve[0] == auth_username and retrieve[1] == auth_password:
                self.IS_ONLINE[sock] = True
                self.clients[sock] = auth_username
                sock.sendall(do_encrypt({'head': 'login', 'body': True}))
            else:
                sock.sendall(do_encrypt({'head': 'login', 'body': False}))
        except TypeError:
            sock.sendall(do_encrypt({'head': 'login', 'body': False}))

    def handle(self, sock):
        # Filters the header of each received message and runs the
        try:
            while True:
                raw_data = sock.recv(1024)
                if not raw_data:
                    break
                data = do_decrypt(raw_data)
                while True:
                    if data['head'] == 'login':
                        self.authenticate_client(sock, data)

                    elif data['head'] == 'bcast':
                        if self.IS_ONLINE[sock]:
                            for clients in self.clients:
                                if clients != sock:
                                    clients.sendall(raw_data)

                    # elif data['head']['dm']:
                    #     pass
                    break
        except ConnectionResetError:
            print('Client disconnected: ', self.clients[sock])
            del self.clients[sock]
            self.IS_ONLINE[sock] = False
        # except ConnectionAbortedError:
        # except EOFError:
        #     pass
        # except KeyError:
        # If is_online == False, shit goes down

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
        enc = do_encrypt(credentials)
        self.sock.sendall(enc)
        data = self.sock.recv(1024)
        result = do_decrypt(data)
        if result['body']:
            return True
        else:
            return False

    def handle(self):
        """ threaded: will loop for broadcasted messages """
        raw_data = self.sock.recv(1024)
        data = do_decrypt(raw_data)
        return data['body']

        # Implement DM if/elif HERE ------

    def send(self, message):
        """ """
        raw_data = {'head': 'bcast', 'body': message}
        data = do_encrypt(raw_data)
        self.sock.sendall(data)


key = b'\xd94\xe1\x9c\xaa0\xe3:\xa8\x03y\x8a\x12\xd4*!'


def do_encrypt(plaintext):
    global key
    data = bytes(str(plaintext), 'utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    result = pickle.dumps({'iv': iv, 'ciphertext': ct})
    return result


def do_decrypt(ciphertext):
    global key
    try:
        b64 = pickle.loads(ciphertext)
        iv = b64decode(b64['iv'])
        ct = b64decode(b64['ciphertext'])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return eval(pt)

    except ValueError:
        print('ValueError: Incorrect decryption!')
    except KeyError:
        print('keyError: Incorrect decryption!')