from chatserver import ChatServer
import argparse
import pymysql
import logging


def main():
    parser = argparse.ArgumentParser(description="""XYZ Messenger - Secure private chat room service with encrypted communication and user-authentication.""")

    parser.add_argument('-dP', '--dbpassword', metavar='PASSWORD', required=True,
                        help='Enter password for database system-user.')

    parser.add_argument('-dU', '--dbuser', metavar='USER', default='sys-select',
                        help='Database user. (DEFAULT: sys-select)')

    parser.add_argument('-dA', '--dbaddress', metavar='ADDRESS', default='127.0.0.1',
                        help='IP address of database to connect to. (DEFAULT: localhost)')

    parser.add_argument('--database', metavar='NAME', default='chatroom',
                        help='Name of database. (DEFAULT: chatroom)')

    parser.add_argument('-b', '--bind', metavar='(IP, PORT)', default=('127.0.0.1', 60000), type=tuple,
                        help='Specify IP address for chat room socket. (DEFAULT: (localhost, 60000))')

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Specify optional output location for logg messages. (DEFAULT: console)')

    args = parser.parse_args()

    if args.output:
        logging.basicConfig(filename=args.output, level=logging.INFO, format='%(levelname)s:server:%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s:server:%(message)s')

    try:
        logging.info('Authenticating database credentials ...')
        database_sock = pymysql.connect(args.dbaddress, args.dbuser, args.dbpassword, args.database)
        logging.info('Database authenticaton: Successfull!')

    except pymysql.err.OperationalError:
        logging.error(f"Database authentication: Failed: Access denied for user '{args.dbuser}'@'{args.dbaddress}'")
        quit()

    else:
        server = ChatServer(args.bind, database_sock)
        server.start()


if __name__ == '__main__':
    main()