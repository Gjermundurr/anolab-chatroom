import socket
from chatroom.aescipher import do_decrypt, do_encrypt
from chatroom.dhke import DH, DH_MSG_SIZE, LEN_PK


class ClientSock:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 60000))
        self.key = None

    def dh(self):
        """
        Perform Diffie-Hellman Key Exchange with the server.
        p: prime modulus declared by the server
        g: generator declared by the server
        server_key: the server's public key
        private_key: the client's private key
        public_key: the client's public key
        :return shared_key: the 256-bit key both the client and
        server now share
        """
        print("Establishing Encryption Key...")
        dh_message = self.sock.recv(DH_MSG_SIZE)
        # Unpack p, g, and server_key from the server's dh message
        p, g, server_key = DH.unpack(dh_message)
        # Generate a randomized private key
        private_key = DH.gen_private_key()
        # Send the server a public key which used the previously
        # Generated private key and both g and p
        public_key = DH.gen_public_key(g, private_key, p)
        self.sock.sendall(DH.package(public_key, LEN_PK))
        # Calculate shared key
        shared_key = DH.get_shared_key(server_key, private_key, p)
        print("Shared Key: {}".format(shared_key))
        # self.cli.add_msg("Encryption Key: {}".format(binascii.hexlify(shared_key).decode("utf-8")))
        return shared_key

    def start(self):
        try:
            self.key = self.dh()
        except ConnectionError:
            print('unable to connect.')
            return

    def login(self, username, password):
        credentials = {'head': 'login', 'body': (username, password)}
        encrypted_data = do_encrypt(self.key, credentials)
        self.sock.sendall(encrypted_data)
        data = do_decrypt(self.key, self.sock.recv(1024))
        if not data:
            return False
        else:
            return data

    def receiver(self):
        """
        callback function for receiving data from server
        :return: returns the received and decrypted data
        """
        try:
            data = do_decrypt(self.key, self.sock.recv(1024))
            return data
        except ConnectionAbortedError:
            print('ConnectionAbortedError')

        except ConnectionResetError:
            print('Lost connection to server!')

    def send(self, **data):
        if data['head'] == 'bcast':
            data = {'head': 'bcast', 'body': data['message']}

        elif data['head'] == 'dm':
            data = {'head': 'dm', 'body': (data['recipient'], data['sender'], data['message'])}

        self.sock.sendall(do_encrypt(self.key, data))
        print('clientsock.send: ', data)

    def close(self):
        self.sock.shutdown(1)
        # self.sock.close()

