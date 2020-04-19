import pymysql
import bcrypt
HOST = '127.0.0.1'
PORT = 60000


def menu():
    while True:
        print('''
             ### chat room server ###
        ----------------------------------
        1) Add new user to database
        2) ...
        3) ...

        4) Shutdown

        ''')
        select = input('> ')

        if int(select) == 1:
            print('Adding new user to database:')
            get_email = input('Enter users email address:')
            get_username = input('Enter username: ')
            get_password = input('Enter a strong password: ')

            # salt = bcrypt.gensalt()
            salt = '$2b$12$5j4Ce8SPnwfM9FIOtV99C.'
            hashed_password = bcrypt.hashpw(get_password.encode('utf-8'), salt.encode('utf-8'))

            cur = db_sock.cursor()
            query = (
                "INSERT INTO clients (username, password, email)"
                "VALUES (%s, %s, %s)"
            )
            data = (get_username, hashed_password, get_email)
            cur.execute(query, data)
            db_sock.commit()
            print('New user added!')


if __name__ == '__main__':
    db_sock = pymysql.connect('database-1.cpv50obye5su.eu-central-1.rds.amazonaws.com', 'admin', 'password123', 'Chatroom')
    menu()
