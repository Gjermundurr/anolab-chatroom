import argparse

parser = argparse.ArgumentParser(description='Secure chat room service with encrypted communication.')
parser.add_argument('--password', required=True, help='Enter password for database system-user.')

sqlpass = None
args = parser.parse_args()

print(sqlpass)
sqlpass = args['password']
print(args)
print(sqlpass)
