import bcrypt

passwd = b'thisisatest!'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(passwd, salt)

print(salt)
print(hashed)


guess = b'thisisatest'

if bcrypt.checkpw(guess, hashed):
    print('s')