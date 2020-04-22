from chatroom_v2.clientsock import do_decrypt, do_encrypt
import socket
import threading
import pymysql
import pickle

SRV_ADDR = ('127.0.0.1', 60000)
SRV_SOCK_LIMIT = 10
DB_ADDR = '127.0.0.1'
DB_USER = 'server-admin'
DB_PWORD = 'password123'
DB_NAME = 'chatroom'

connected_sockets = {}      # socket: IP
verified = {}               # dict of boolean
clients = {}                # usernames and fullnames

database_sock = pymysql.connect(DB_ADDR, DB_USER, DB_PWORD, DB_NAME)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(SRV_ADDR)
server_sock.listen(SRV_SOCK_LIMIT)


def authenticate(sock):
    global verified, clients
    data = do_decrypt(client_sock.recv(1024))
    username = data['body'][0]
    password = data['body'][1].decode('utf-8')

    with database_sock.cursor() as cursor:
        query = "SELECT user_id, username, password FROM users where username=%s"
        values = (username,)
        cursor.execute(query, values)
        retrieve = cursor.fetchone()

    if retrieve is None:
        sock.sendall(do_encrypt({'head': 'login', 'body': False}))
        sock.close()

    elif retrieve[1] == username and retrieve[2] == password:
        sock.sendall(do_encrypt({'head': 'login', 'body': True}))
        verified[username] = True
        with database_sock.cursor() as cursor:
            query = "SELECT fullname FROM clients where user_id=%s"
            values = (retrieve[0],)
            cursor.execute(query, values)
            retrieve = cursor.fetchone()
            clients[username] = retrieve[0]
        return True

    else:
        sock.sendall(do_encrypt({'head': 'login', 'body': False}))
        return False


def handle(sock):
    global connected_sockets
    if authenticate(sock):
        try:
            while True:
                raw_data = sock.recv(1024)
                print(raw_data)
                data = do_decrypt(raw_data)
                if data['head'] == 'bcast':
                    for users in connected_sockets:
                        if users != sock:
                            users.sendall(raw_data)

                elif data['head'] == 'dm':
                    direct_message(sock, data)
                pass
        except ConnectionResetError:
            print('Disconnected: ', sock)

def direct_message(sock, data):
    pass


while True:
    client_sock, client_address = server_sock.accept()
    connected_sockets[client_sock] = client_address
    threading.Thread(target=handle, args=(client_sock,), daemon=True).start()
