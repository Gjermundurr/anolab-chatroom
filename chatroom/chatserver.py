from aescipher import do_encrypt, do_decrypt
from dhke import DH, DH_SIZE, LEN_PK
from M2Crypto import DH as M2DH
import bcrypt
import socket
import pymysql
import threading
import time
import logging


class ChatServer:
    def __init__(self, bind_address, database):
        self.database_sock = database
        self.address = bind_address
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print("Generating a {}-bit prime...".format(DH_SIZE))
        logging.info("Generating a {}-bit prime...".format(DH_SIZE))
        self.dh_params = M2DH.gen_params(DH_SIZE, 2)
        #print('done!')
        logging.info('done!')
        self.clients = []           # List of all connected clients.
        self.is_online_flag = []    # Flag used by ChatServer.is_online method.

    def authenticate(self, client):
        """ Receive client username/password and compare credentials with backend database.
        The method receives login credentials from the connected client and compares the received credentials with the
        user data stored in the database.

        The method has three outcomes:
            1. The received username does not match any entries in the chatroom.users table.
                result: server sends a False boolean back to client application.

            2. the received username matches with a table entry but the password hash comparison fails.
                result: server sends a False boolean back to client application.

            3. The received username matches with a table entry and the password hash comparison is successful.
                result: servers sends a True boolean and the client's full name back to client application.

        :param client: Client class object established upon connection to server.
        """
        while True:
            try:
                data = do_decrypt(client.key, client.sock.recv(1024))
                # Unpack received login credentials from the connected client.
                username = data['body'][0]
                password = data['body'][1]
            except (ConnectionResetError, TypeError):
                client.sock.close()
                break

            with self.database_sock.cursor() as cursor:
                # A SELECT query is performed to return user_id, username, and hashed password from the database,
                # based upon the username sent by the connected client. If the received username does not match any
                # table entries, the query will return a NoneType object which and is handled by the try/except
                # clause below.
                query = "SELECT USER_NAME, PASSWORD, FULL_NAME FROM users where USER_NAME=%s"
                values = (username,)
                cursor.execute(query, values)
                
            try:
                # Unpacking successful database query results
                ret_username, ret_password, ret_fullname = cursor.fetchone()

                # Using bcrypt module to perform a hash comparison with on the password hash from the database and
                # the submitted password from the client. The client is successfully authenticated if both the
                # password and username matches the database entry.
                if bcrypt.checkpw(password.encode('utf-8'), ret_password.encode('utf-8')) and ret_username == username:
                    # the class object's attributes are updated accordingly and the connected client recieves his
                    # full name and a boolean signaling the GUI application to enter the MainPage.
                    client.fullname = ret_fullname
                    client.username = username
                    send = {'head': 'login', 'body': (True, ret_fullname)}
                    client.sock.sendall(do_encrypt(client.key, send))
                    self.clients.append(client)
                    self.is_online_flag.append(username)
                    client.state = 1
                    logging.info(f'Client authenticated: {client.username}@{client.address[0]}')
                    return True

                else:
                    # else statement is executed if the password does not match with the hash stored in the database.
                    logging.warning(f'Authentication failed: {client.username}@{client.address[0]}')
                    send = {'head': 'login', 'body': (False,)}
                    client.sock.sendall(do_encrypt(client.key, send))
                    continue

            except TypeError:
                logging.warning(f'Authentication failed: {client.username}@{client.address[0]}')
                send = {'head': 'login', 'body': (False,)}
                client.sock.sendall(do_encrypt(client.key, send))
                continue

    def disconnect(self, client):
        """ Remove a client from inventory and close the socket. A client has either executed a socket.shutdown(1)
        and is waiting for a (FIN - ACK) or the client application has been killed. Either way, the socket is closed
        and the client's class object is deleted.

        When a client disconnects, the server sends a special hidden message out to every connection to update the
        client applications 'online users' side panel. This message is handled by the clients
        MainWindow.is_online method.
        """

        client.sock.close()
        send = {'head': 'meta', 'body': {'offline': client.fullname}}
        for user in self.clients:
            if user != client:
                user.sock.sendall(do_encrypt(user.key, send))
        self.clients.remove(client)
        logging.info(f'Client disconnected: {client.username}@{client.address[0]}')

    def handle(self, client):
        """ The main thread to each connection. will continuously receive messages from a client and perform an
        operation based on the header value. if header value reads 'bcast', the message is to be sent to every
        connected client. if header value reads 'dm', the message is private between two clients and is only sent to
        the user matching the tuple index[1].

        Message examples:
        data = {'head': 'bcast', 'body': ('ExampleUSer1', 'This is my message to be broadcast!')}
        data = {'head': 'dm', 'body': ('TO_ExampleUSer1', 'FROM_ExampleUser2', 'Hello, this is a private message.')}
        """
        if self.authenticate(client):
            try:
                while True:
                    data = do_decrypt(client.key, client.sock.recv(1024))

                    if data is None:
                        self.disconnect(client)
                        break

                    if data['head'] == 'bcast':
                        for user in self.clients:
                            if user != client:
                                user.sock.sendall(do_encrypt(user.key, data))

                    elif data['head'] == 'dm':
                        for user in self.clients:
                            if user.fullname == data['body'][0]:
                                user.sock.sendall(do_encrypt(user.key, data))

            except ConnectionResetError:
                self.disconnect(client)

    def is_online(self):
        """ Broadcasts hidden messages to all connected clients containing information of who is online.
        The method is a loop with a two seconds sleep interval and use the Client.state attribute. When a client
        successfully authenticates, his state is first set to 1. This indicates that the client has no prior data of
        who else is currently connected to the chat room. The method then creates a list containing the fullname of
        all currently connected clients and sends it out to the client. The new client is now up-to-date with the
        rest of the connected clients and can be put in state 2.

        State two is triggered by a new connection setting the is_online_flag to True and creates a list of the newly
        connected clients (which would have state 1) and sends it out to all previous connections, allowing them to
        update their display of online clients.

        State 1: Receives list containing fullname of all current connections.
        State 2: Receives list containing fullname of the new connections.

        Example meta message:
        data = {'head': 'meta', 'body': {'online': ['ExampleName1', ExampleName2', 'ExampleName3']}}
        """
        while True:
            time.sleep(2)
            clients = self.clients.copy()
            # Triggered by a new connection, sends out the fullname of the new client to all
            # previously connected clients.
            if self.is_online_flag:
                for user in clients:
                    if user.state == 2:
                        online = [client.fullname for client in clients if client.state == 1]
                        data = {'head': 'meta', 'body': {'online': online}}
                        user.sock.sendall(do_encrypt(user.key, data))
                self.is_online_flag.clear()

            # Sends out a list containing fullname of all connected clients, to the new client.
            for user in clients:
                if user.state == 1:
                    online = [client.fullname for client in clients]
                    data = {'head': 'meta', 'body': {'online': online}}
                    user.sock.sendall(do_encrypt(user.key, data))
                    user.state = 2

    def start(self):
        """ Starts the chat room server.
        Binds the IP address to a socket object and starts listening for
        connections, and executes the is_online method as a daemon thread. The loop accepts a new connection and
        creates a Client class-object, containing all relevant data to the connection. The initializer of the Client
        class will establish a symmetrical encryption key between the server and client before passing the new client
        object onwards to the authentication step found in the handle.
        """
        self.server_sock.bind(self.address)
        logging.info(f'Binding IP {self.address} to socket ...')
        self.server_sock.listen(25) # 25 = backlog limit
        threading.Thread(target=self.is_online, args=(), daemon=True).start()
        logging.info('Listening for incomming connections!')
        while True:
            client_sock, client_address = self.server_sock.accept()
            logging.info(f'Connection established: {client_address[0]}:{client_address[1]}')
            # Create client object and establish encryption key.
            client = Client(self, client_sock, client_address)
            # Close connection if Diffie-Hellman algorithm fails.
            if not client.key:
                client.sock.close()
                logging.warning('Diffie-Hellman key exchange failed, closing connection!')
                continue
            # Encryption key is established and secure communication can be ensured.
            # Handle method is threaded to allow multiple connections and begins the authentication process.
            threading.Thread(target=self.handle, args=(client,), daemon=True).start()


class Client:
    def __init__(self, chatserver, sock, address):
        """ Template for each new connection with attributes containing data related to each unique connection.

        :param chatserver: passed to Diffie Hellman algorithm to establish a unique encryption key with each client.
        :param sock: socket object
        :param address: IP and PORT address
        """
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
            logging.error(f"Key Exchange with {self.address[0]} failed")
            return None
        client_key = DH.b2i(response)
        # Calculate shared key with newly received client key
        shared_key = DH.get_shared_key(client_key, a, p)
        return shared_key
