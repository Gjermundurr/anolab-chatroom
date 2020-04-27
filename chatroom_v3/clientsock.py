import socket
import bcrypt  # remove?
from chatroom_v3.aescipher import AESchiper


class ClientSock:
    DESTINATION_ADDR = ('127.0.0.1', 60000)

    def __init__(self):
        self.cipher = AESchiper()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def login(self, username, password):
        salt = '$2b$12$5j4Ce8SPnwfM9FIOtV99C.'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
        credentials = {'head': 'login', 'body': (username, hashed_password)}
        encrypted_data = self.cipher.do_encrypt(credentials)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(ClientSock.DESTINATION_ADDR)
        self.sock.sendall(encrypted_data)
        return self.cipher.do_decrypt((self.sock.recv(1024)))

    def receiver(self):
        try:
            data = self.cipher.do_decrypt(self.sock.recv(1024))
            return data
        except ConnectionAbortedError:
            pass
        except ConnectionResetError:
            print('Lost connection to server')

    def send_bcast(self, message):
        data = {'head': 'bcast', 'body': message}
        self.sock.sendall(self.cipher.do_encrypt(data))

    def send_dm(self):
        pass

    def close(self):
        self.sock.close()

