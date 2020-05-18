import configparser


config = configparser.ConfigParser()

config.read(r'C:\Users\Jerry\VCS\chatroom\chatroom\config.txt')
print(config.sections())
print(config['default']['host'])