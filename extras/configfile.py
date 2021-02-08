from configparser import ConfigParser

config_object = ConfigParser()

config_object['DATABASECONFIG'] = {
    'address': '127.0.0.1',
    'user': '123123',
    'password': 'abc123123',
    'dbname': '123123'
}

config_object['SERVERCONFIG'] = {
    'address': '123123123',
    'port': 123123,
    'log_file': '/var/log/chatroom/server.log'
}

with open('config.ini', 'w') as conf:
    config_object.write(conf)