import socket
import pickle
import bcrypt  # remove?
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# from Crypto.Random import get_random_bytes


class ClientSock:
    DESTINATION_ADDR = ('127.0.0.1', 60000)

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def login(self, username, password):
        salt = '$2b$12$5j4Ce8SPnwfM9FIOtV99C.'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
        credentials = {'head': 'login', 'body': (username, hashed_password)}
        encrypted_data = do_encrypt(credentials)

        self.sock.connect(ClientSock.DESTINATION_ADDR)
        self.sock.sendall(encrypted_data)
        return do_decrypt((self.sock.recv(1024)))

    def receiver(self):
        try:
            data = do_decrypt(self.sock.recv(1024))
            return data
        except ConnectionAbortedError:
            pass
        except ConnectionResetError:
            print('Lost connection to server')

    def send_bcast(self, message):
        data = {'head': 'bcast', 'body': message}
        self.sock.sendall(do_encrypt(data))

    def send_dm(self):
        pass

    def close(self):
        self.sock.close()


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
