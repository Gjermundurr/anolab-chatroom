from modules.chatserver import ChatServer
import pymysql
import logging 

log_file = '/var/log/chatroom/server.log'

if open(log_file, 'r'):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(levelname)s:server:%(message)s')

else:
    open(log_file, 'x')
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(levelname)s:server:%(message)s')



database_sock = pymysql.connect('127.0.0.1', 'sys-select', '420!Du!kommer!aldri!til!a!klare!det', 'chatroom')
print('Database: Connected!')
server = ChatServer(('188.166.75.232', 42066), database_sock)
try:
    server.start()

except KeyboardInterrupt:
    print('Stopping server.')