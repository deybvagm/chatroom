from nacl import pwhash
from nacl.exceptions import InvalidkeyError

import logging
LOGGER = logging.getLogger(__name__)

SQL_LOGIN_STATEMENT = "SELECT password FROM participant WHERE username = %(username)s"


class AuthHandler:
    def __init__(self, store_handler):
        self.store = store_handler

    def validate_authentication(self, username, unchecked_pass):
        params = {'username': username}
        try:
            resp = self.store.query(SQL_LOGIN_STATEMENT, params)
            if resp is not None:
                passw_hash, = resp
                auth_decision = pwhash.argon2id.verify(bytes(passw_hash, 'utf-8'), bytes(unchecked_pass, 'utf-8'))
                return True if auth_decision else False
            return False
        except InvalidkeyError as e:
            LOGGER.warning('[AuthHandler] Exception validating credentials for user {}, reason: {}'.format(username, e))
            return False
        except Exception as e:
            LOGGER.error('[AuthHandler] An error occurred while connecting to the database', e)
            return False
