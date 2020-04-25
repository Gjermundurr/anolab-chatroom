from chatroom_v2.clientsock import do_decrypt, do_encrypt
import socket
import threading
import pymysql

SRV_ADDR = ('127.0.0.1', 60000)
SRV_SOCK_LIMIT = 10
DB_ADDR = '127.0.0.1'
DB_USER = 'server-admin'
DB_PWORD = 'password123'
DB_NAME = 'chatroom'

database_sock = pymysql.connect(DB_ADDR, DB_USER, DB_PWORD, DB_NAME)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(SRV_ADDR)
server_sock.listen(SRV_SOCK_LIMIT)
clients = {}
offline = []


def authenticate(sock):
    global clients
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
        del clients[sock]
        return False

    elif retrieve[1] == username and retrieve[2] == password:
        with database_sock.cursor() as cursor:
            query = "SELECT fullname FROM clients where user_id=%s"
            values = (retrieve[0],)
            cursor.execute(query, values)
            retrieve = cursor.fetchone()
        clients[sock] = {'username': username, 'fullname': retrieve[0], 'state': 0}
        sock.sendall(do_encrypt({'head': 'login', 'body': (True, retrieve[0])}))
        return True


def handle(sock):
    global clients
    if authenticate(sock):
        threading.Thread(target=is_online(sock)
        try:
            while True:
                raw_data = sock.recv(1024)
                data = do_decrypt(raw_data)
                if data['head'] == 'bcast':
                    for client in clients:
                        if client != sock:
                            client.sendall(raw_data)

                elif data['head'] == 'dm':
                    pass

        except ConnectionResetError:
            print('Disconnected: ', sock)
            for client in clients:
                if client != sock:
                    client.sendall(do_encrypt({'head': 'meta', 'body':  {'offline': [clients[sock]['fullname']]}}))
                    del clients[sock]


def is_online(sock):
    global clients
    online = [client['fullname'] for client in clients.values()]
    if clients[sock]['state'] == 0 or clients[sock]['state'] == 1:
        body = {'online': online, 'offline': None}
        sock.sendall(do_encrypt({'head': 'meta', 'body': body}))


if __name__ == '__main__':
    # threading.Thread(target=is_online, args=(), daemon=True).start()
    while True:
        client_sock, client_address = server_sock.accept()
        clients[client_sock] = client_address
        threading.Thread(target=handle, args=(client_sock,), daemon=True).start()
