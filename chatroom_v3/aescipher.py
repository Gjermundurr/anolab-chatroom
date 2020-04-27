import pickle
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
# from Crypto.Random import get_random_bytes


class AESchiper:
    def __init__(self):
        self.key = b'\xd94\xe1\x9c\xaa0\xe3:\xa8\x03y\x8a\x12\xd4*!'

    def do_encrypt(self, plaintext):
        data = bytes(str(plaintext), 'utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        result = pickle.dumps({'iv': iv, 'ciphertext': ct})
        return result

    def do_decrypt(self, ciphertext):
        try:
            b64 = pickle.loads(ciphertext)
            iv = b64decode(b64['iv'])
            ct = b64decode(b64['ciphertext'])
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return eval(pt)
        except ValueError:
            print('ValueError: Incorrect decryption!')
        except KeyError:
            print('keyError: Incorrect decryption!')
