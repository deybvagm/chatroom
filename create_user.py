from nacl import pwhash
import argparse
from db.db_connector import DBConnector


sql = """
INSERT INTO participant(username, password)
VALUES (%(username)s, %(password)s)
"""

config = {
    'host': 'localhost',
    'name': 'chatroomdb',
    'user': 'chatroom',
    'password': 'chatroom'
}
db = DBConnector(config)

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', type=str, help="username to register in db")
parser.add_argument("-p", "--password", help='password to register in db')
args = parser.parse_args()

username = args.user
password = pwhash.argon2id.str(bytes(args.password, 'utf-8'))

params = {
    'username': args.user,
    'password': password.decode("utf-8")
}
db.save(sql, params)



