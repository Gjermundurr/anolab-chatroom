from chatserver import ChatServer
import pymysql

database_sock = pymysql.connect('127.0.0.1', 'sys-select', '420!Du!kommer!aldri!til!a!klare!det', 'chatroom')
print('Database: Connected!')
server = ChatServer(('188.166.75.232', 42066), database_sock)
server.start()
print('Successfully launching server!')
