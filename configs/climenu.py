import pymysql
import bcrypt
from getpass import getpass


def menu():
    print("""
    Welcome to XYZ Messenger CLI-menu!
    Please enter database credentials:
    """)
    dbuser = input('Username: ')
    dbpass = getpass()
    
    try:
        db_sock = pymysql.connect('localhost', dbuser, dbpass, 'chatroom')
    
    except pymysql.err.OperationalError:
        print(f"Access denied for user '{dbuser}'@'localhost'.")
        quit()

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
            get_email = input('Enter users email address:')             # Get email address
            get_fullname = input('Enter full name: ')                   # Get full name
            print('~~ Create username and password ~~')
            get_username = input('Enter username: ')                    # Set username
            get_password = getpass(prompt='Enter a strong password: ')  # Set password

            salt = bcrypt.gensalt()                                              # Generate random salt value
            hashed_password = bcrypt.hashpw(get_password.encode('utf-8'), salt)  # create password hash

            cur = db_sock.cursor()
            # Database query
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
    menu()
