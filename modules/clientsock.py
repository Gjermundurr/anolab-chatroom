import socket
from modules.aescipher import do_decrypt, do_encrypt
from modules.dhke import DH, DH_MSG_SIZE, LEN_PK


class ClientSock:
    """ Class defining spesific operations regarding the client applications socket object.
        The class is imported by clientapp.py and used appropriately.
        The class includes methods for establishing a connection to the server and performing the DH-KE.
        Next, the client uses the Login method to send his encrypted credentials for authentication.
        The last three methods are for constructing messages following the chat rooms standards, receiving
        data, and closing the socket connection the correct way.  
    """
    def __init__(self, server_ip:tuple):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip      # IP address to connect to.
        self.key = None                 # Symmetrical-key produced by DHKE.

    def dh(self):
        """ Perform Diffie-Hellman Key Exchange with the server.
            p: prime modulus declared by the server
            g: generator declared by the server
            server_key: the server's public key
            private_key: the client's private key
            public_key: the client's public key
            :return shared_key: the 256-bit key both the client and server now share
        """

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
        return shared_key

    def start(self):
        """ Connect to the server's IP address followed by the Diffie-Hellman Key Exchange.
        """
        self.sock.connect(self.server_ip)
        self.key = self.dh()
        
    def login(self, username, password):
        """ Receives the user's credentials from Login page and packages the information
            using the set message standard. Enryption is applied and the ciphertext is sent to the server for authentication.
            The server replies with a boolean indicating success or failiure.
        """
        credentials = {'head': 'login', 'body': (username, password)}
        encrypted_data = do_encrypt(self.key, credentials)
        self.sock.sendall(encrypted_data)
        data = do_decrypt(self.key, self.sock.recv(4096))
        if not data:
            return False
        else:
            return data

    def receiver(self):
        """ Method for receiving and decryting data, called by client's handle method.
            If connection is dropped the method returns a string which will trigger a message box in the applicaton.
        """
        try:
            data = do_decrypt(self.key, self.sock.recv(4096))
            return data
            
        except ConnectionAbortedError:
            return 'ConnectionError'

        except ConnectionResetError:
            return 'ConnectionError'

    def send(self, **data):
        """ Create structured message objects and send to the server.
            Messages are constructed using nested dictionaries and container types to indicate the purpose and destination of a message.
            Using dictionaries and key/value pairs, every message is constructed with a head & body field. The header indicates the type
            of message and can be either a broadcast for all to receive or a direct message with a single destination.
            The body field contains the written message and in the case of Dm's includes the names of the message's recipient and sender.

            Example messages:
                Broadcasted message ==  {'head': 'bcast', 'body': TextObject}
                Direct message      ==  {'head': 'dm', 'body': ('NameOfDestination, NameOfSource, TextObject)}
            
        """
        try:
            if data['head'] == 'bcast':
                data = {'head': 'bcast', 'body': data['message']}

            elif data['head'] == 'dm':
                data = {'head': 'dm', 'body': (data['recipient'], data['sender'], data['message'])}

            self.sock.sendall(do_encrypt(self.key, data))
        
        except ConnectionAbortedError:
            return # server has disconneced or stopped

    def close(self):
        """ Appropriatly close the TCP connection by signaling to the server that no more data is to be sent
            and the connection can be closed.
        """
        self.sock.shutdown(1)
