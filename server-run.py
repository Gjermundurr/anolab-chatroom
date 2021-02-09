#!/usr/bin/env python3
from modules.chatserver import ChatServer
from configparser import ConfigParser
import pymysql
import logging 


# read config file
config_object = ConfigParser()
config_object.read('config.ini')
databaseconf = config_object['DATABASECONFIG']
serverconf = config_object['SERVERCONFIG']

if open(serverconf['log_file'], 'r'):
    logging.basicConfig(filename=serverconf['log_file'], level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

else:
    open(serverconf['log_file'], 'x')
    logging.basicConfig(filename=serverconf['log_file'], level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')


database_sock = pymysql.connect(databaseconf['address'], databaseconf['user'], databaseconf['password'], databaseconf['dbname'])
print('Database: Connected!')
logging.info('Database connected!')
server = ChatServer((serverconf['address'], int(serverconf['port'])), database_sock)
try:
    server.start()

except KeyboardInterrupt:
    logging.info('Stopping server.\n')