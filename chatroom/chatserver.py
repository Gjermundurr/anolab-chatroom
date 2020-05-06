from chatroom.aescipher import do_encrypt, do_decrypt
from chatroom.dhke import DH, DH_SIZE, LEN_PK
from M2Crypto import DH as M2DH
import bcrypt
import socket
import pymysql
import threading
import time


class ChatServer:
    SRV_ADDR = ('127.0.0.1', 60000)
    SRV_SOCK_LIMIT = 10
    DB_ADDR = '127.0.0.1'
    DB_USER = 'server-admin'
    DB_PWORD = 'password123'
    DB_NAME = 'chatroom'

    def __init__(self):
        self.database_sock = pymysql.connect(self.DB_ADDR, self.DB_USER, self.DB_PWORD, self.DB_NAME)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Generating a {}-bit prime...".format(DH_SIZE))
        self.dh_params = M2DH.gen_params(DH_SIZE, 2)
        print('done!')
        self.clients = []
        self.is_online_flag = []

    def authenticate(self, client):
        while True:
            try:
                data = do_decrypt(client.key, client.sock.recv(1024))
            except ConnectionResetError:
                client.sock.close()
                break

            username = data['body'][0]
            password = data['body'][1]

            with self.database_sock.cursor() as cursor:
                query = "SELECT user_id, username, password FROM users where username=%s"
                values = (username,)
                cursor.execute(query, values)
                retrieve = cursor.fetchone()
            try:
                ret_id, ret_username, ret_password = retrieve
                if bcrypt.checkpw(password.encode('utf-8'), ret_password.encode('utf-8')) and ret_username == username:
                    with self.database_sock.cursor() as cursor:
                        query = "SELECT fullname FROM clients where user_id=%s"
                        values = (ret_id,)
                        cursor.execute(query, values)
                        fullname = cursor.fetchone()

                    client.fullname = fullname[0]
                    client.username = username
                    send = {'head': 'login', 'body': (True, fullname)}
                    client.sock.sendall(do_encrypt(client.key, send))
                    self.clients.append(client)
                    self.is_online_flag.append(username)
                    client.state = 1
                    print('Authenticated: ', client.address)
                    return True
                else:
                    print('authentication failed')
                    send = {'head': 'login', 'body': (False,)}
                    client.sock.sendall(do_encrypt(client.key, send))
                    continue
            except TypeError:
                print('authentication failed')
                send = {'head': 'login', 'body': (False,)}
                client.sock.sendall(do_encrypt(client.key, send))
                continue

    def disconnect(self, client):
        """ client has either sent a socket.shutdown(1) or killed client-process. Either way, the socket is closed
        and total connections is updated. """

        client.sock.close()
        send = {'head': 'meta', 'body': {'offline': client.fullname}}
        for user in self.clients:
            if user != client:
                user.sock.sendall(do_encrypt(user.key, send))
        self.clients.remove(client)
        print('Disconnected: ', client.address)

    def handle(self, client):
        if self.authenticate(client):
            try:
                while True:
                    data = do_decrypt(client.key, client.sock.recv(1024))
                    if data is None:
                        self.disconnect(client)
                        break

                    print('handle: ', data)
                    if data['head'] == 'bcast':
                        for user in self.clients:
                            if user != client:
                                user.sock.sendall(do_encrypt(user.key, data))

                    elif data['head'] == 'dm':
                        for client in self.clients:
                            if client.fullname == data['body'][0]:
                                client.sock.sendall(do_encrypt(client.key, data))
                                print(f'sending DM to: {client.fullname}')

            except ConnectionResetError:
                self.disconnect(client)

    def is_online(self):
        while True:
            time.sleep(2)
            clients = self.clients.copy()
            if self.is_online_flag:
                for user in clients:
                    if user.state == 2:
                        online = [client.fullname for client in clients if client.state == 1]
                        data = {'head': 'meta', 'body': {'online': online}}
                        user.sock.sendall(do_encrypt(user.key, data))
                self.is_online_flag.clear()

            for user in clients:
                if user.state == 1:
                    online = [client.fullname for client in clients]
                    data = {'head': 'meta', 'body': {'online': online}}
                    user.sock.sendall(do_encrypt(user.key, data))
                    user.state = 2

    def run(self):
        self.server_sock.bind(self.SRV_ADDR)
        self.server_sock.listen(self.SRV_SOCK_LIMIT)
        threading.Thread(target=self.is_online, args=(), daemon=True).start()
        while True:
            client_sock, client_address = self.server_sock.accept()
            client = Client(self, client_sock, client_address)
            if not client.key:
                client.sock.close()
                print('key exchange failed!')
                continue
            threading.Thread(target=self.handle, args=(client,), daemon=True).start()


class Client:
    def __init__(self, chatserver, sock, address):
        self.sock = sock
        self.address = address
        self.key = self.dh(chatserver.dh_params)
        self.state = 0
        self.username = None
        self.fullname = None

    def dh(self, dh_params):
        """
        Perform Diffie-Hellman Key Exchange with a client.
        :param dh_params: p and g generated by DH
        :return shared_key: shared encryption key for AES
        """
        # p: shared prime
        p = DH.b2i(dh_params.p)
        # g: primitive root modulo
        g = DH.b2i(dh_params.g)
        # a: randomized private key
        a = DH.gen_private_key()
        # Generate public key from p, g, and a
        public_key = DH.gen_public_key(g, a, p)
        # Create a DH message to send to client as bytes
        dh_message = bytes(DH(p, g, public_key))
        self.sock.sendall(dh_message)
        # Receive public key from client as bytes
        try:
            response = self.sock.recv(LEN_PK)
        except ConnectionError:
            print("Key Exchange with {} failed".format(self.address[0]))
            return None
        client_key = DH.b2i(response)
        # Calculate shared key with newly received client key
        shared_key = DH.get_shared_key(client_key, a, p)
        return shared_key


if __name__ == '__main__':
    server = ChatServer()
    server.run()
