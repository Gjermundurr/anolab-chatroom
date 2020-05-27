import pymysql
import bcrypt


def menu():
    while True:
        print('''
             ### chat room server ###
        ----------------------------------
        1) Add new user to database
        2) ...
        3) ...

        4) Exit

        ''')
        select = input('> ')

        if int(select) == 1:
            print('Adding new user to database:')
            get_email = input('Enter users email address:')
            get_fullname = input('Enter full name: ')
            print('~~ Create username and password ~~')
            get_username = input('Enter username: ')
            get_password = input('Enter a strong password: ')

            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(get_password.encode('utf-8'), salt)

            cur = db_sock.cursor()
            query = (
                "INSERT INTO users (USER_NAME, PASSWORD, FULL_NAME, EMAIL_ADDRESS) VALUES (%s, %s, %s, %s)"
                     )
            data = (get_username, hashed_password, get_fullname, get_email)
            cur.execute(query, data)
            
            # save changes to database
            db_sock.commit()
            print('New user added!')

        elif int(select) == 4:
            print('Exiting ...')
            db_sock.close()
            quit()


if __name__ == '__main__':
    db_sock = pymysql.connect('localhost', 'server-admin', 'password123', 'chatroom')
    menu()
