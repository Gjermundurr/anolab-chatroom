string1 = 'this is encoded with utf 8'
string2 = 'this is a normal string'
string3 = 'this is decoded with utf8'.encode('utf8')
print(string1)
print(string1.encode('utf-8'))
print(type(string1))
print(string3.decode('utf8'))