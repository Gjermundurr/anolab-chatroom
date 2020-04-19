from Crypto.Cipher import AES
from base64 import b64encode
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import pickle
import socket

# Client:
# send server encrypted msg


data = b"{'head':'bcast', 'body': 'jerry: This is wack!'}"
# key = get_random_bytes(16)
key = b'\xd94\xe1\x9c\xaa0\xe3:\xa8\x03y\x8a\x12\xd4*!'
cipher = AES.new(key, AES.MODE_CBC)
ct_bytes = cipher.encrypt(pad(data, AES.block_size))
iv = b64encode(cipher.iv).decode('utf-8')
ct = b64encode(ct_bytes).decode('utf-8')
result = pickle.dumps({'iv': iv, 'ciphertext': ct})


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 60000))

data = s.sendall(result)

a = 'tst'
b = bytes(a, 'utf-8')
print(b)