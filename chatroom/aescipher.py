import pickle
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# AES-256 CTR cipher suite:

def do_encrypt(key, plaintext):
    data = bytes(str(plaintext), 'utf-8')
    cipher = AES.new(key, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(data)
    nonce = b64encode(cipher.nonce).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    result = pickle.dumps({'nonce': nonce, 'ct': ct})
    return result


def do_decrypt(key, ciphertext):
    try:
        b64 = pickle.loads(ciphertext)
        nonce = b64decode(b64['nonce'])
        ct = b64decode(b64['ct'])
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        pt = cipher.decrypt(ct)
        return eval(pt)
    except ValueError:
        print('Incorrect decryption')
    except KeyError:
        print('Incorrect decryption')
    except EOFError:
        # User has disconnected
        return