from Crypto.Cipher import AES



message = 'This is my super secret message!!!!!'

key = 'this is my test eddddddddddddddd'
obj = AES.new(key, AES.MODE_ECB)

def pad(s):
    return s + ((16-len(s) % 16) * '{')


def encrypt(plaintext):
    global obj
    return obj.encrypt(pad(plaintext).encode('utf-8'))


def decrypt(chipertext):
    global obj
    dec = chiper.decrypt(chipertext).decode('utf-8')
    l = dec.count('{')
    return dec[:len(dec)-1]

print(message)
encrypted = encrypt(message)
decrypted = decrypt(encrypted)
print(encrypted)
print(decrypted)







