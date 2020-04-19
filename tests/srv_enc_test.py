import socket
import pickle
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes


# Server:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 60000))
s.listen(1)

conn, addr = s.accept()
data = conn.recv(1024)
print('Before: ', data)
key = b'\xd94\xe1\x9c\xaa0\xe3:\xa8\x03y\x8a\x12\xd4*!'

try:
    b64 = pickle.loads(data)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    print(iv, ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    print(pt)
except ValueError:
    print('Incorrect decryption')
except KeyError:
    print('Incorrect decryption!')