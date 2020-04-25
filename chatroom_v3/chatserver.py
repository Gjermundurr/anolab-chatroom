from chatroom_v3.operations import AESchiper
import socket
import pymysql
import threading
import time


class ChatServer:
    SRV_ADDR = ('127.0.0.1', 60000)
    SRV_SOCK_LIMIT = 10
    DB_ADDR = '127.0.0.1'
    DB_USER = 'server-admin'
    DB_PWORD = 'password123'
    DB_NAME = 'chatroom'

    def __init__(self):
        self.database_sock = pymysql.connect(self.DB_ADDR, self.DB_USER, self.DB_PWORD, self.DB_NAME)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(self.SRV_ADDR)
        self.server_sock.listen(self.SRV_SOCK_LIMIT)
        self.clients = {}
        self.is_online_flag = []

    def authenticate(self, sock):
        data = cipher.do_decrypt(sock.recv(1024))
        username = data['body'][0]
        password = data['body'][1].decode('utf-8')

        with self.database_sock.cursor() as cursor:
            query = "SELECT user_id, username, password FROM users where username=%s"
            values = (username,)
            cursor.execute(query, values)
            retrieve = cursor.fetchone()

        if retrieve is None:
            send = {'head': 'login', 'body': False}
            sock.sendall(cipher.do_encrypt(send))
            sock.close()
            del self.clients[sock]
            return False

        elif retrieve[1] == username and retrieve[2] == password:
            with self.database_sock.cursor() as cursor:
                query = "SELECT fullname FROM clients where user_id=%s"
                values = (retrieve[0],)
                cursor.execute(query, values)
                retrieve = cursor.fetchone()
            self.clients[sock] = {'username': username, 'fullname': retrieve[0], 'state': 0}
            send = {'head': 'login', 'body': (True, retrieve[0])}
            sock.sendall(cipher.do_encrypt(send))
            self.is_online_flag.append(username)
            return True

    def handle(self, sock):
        if self.authenticate(sock):
            try:
                while True:
                    raw_data = sock.recv(1024)
                    data = cipher.do_decrypt(raw_data)
                    if data['head'] == 'bcast':
                        for client in self.clients:
                            if client != sock:
                                client.sendall(raw_data)

                    elif data['head'] == 'dm':
                        pass

            except ConnectionResetError:
                print('Disconnected: ', sock)
                clients = self.clients.copy()
                send = {'head': 'meta', 'body': {'offline': [clients[sock]['fullname']]}}
                for client in clients:
                    if client != sock:
                        client.sendall(cipher.do_encrypt(send))
                del self.clients[sock]

    def is_online(self):
        while True:
            time.sleep(2)
            clients = self.clients.copy()
            if self.is_online_flag:
                for sock, state in clients.items():
                    if state['state'] == 1:
                        online = [client['fullname'] for client in clients.values() if client['state'] == 0]
                        data = {'head': 'meta', 'body': {'online': online}}
                        sock.sendall(cipher.do_encrypt(data))
                self.is_online_flag.clear()

            for sock, state in clients.items():
                if state['state'] == 0:
                    online = [client['fullname'] for client in clients.values()]
                    data = {'head': 'meta', 'body': {'online': online}}
                    sock.sendall(cipher.do_encrypt(data))
                    state['state'] = 1

    def run(self):
        threading.Thread(target=self.is_online, args=(), daemon=True).start()
        while True:
            client_sock, client_address = self.server_sock.accept()
            self.clients[client_sock] = client_address
            threading.Thread(target=self.handle, args=(client_sock,), daemon=True).start()


if __name__ == '__main__':
    cipher = AESchiper()
    server = ChatServer()
    server.run()
