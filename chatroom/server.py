from chatroom.chatroomsock import ServerSock
HOST = '127.0.0.1'
PORT = 60000


if __name__ == '__main__':
    server_sock = ServerSock()
    server_sock.run(HOST, PORT)
