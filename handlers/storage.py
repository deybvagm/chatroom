import logging
LOGGER = logging.getLogger(__name__)


class Storage:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def save_message(self, params):
        query = 'INSERT INTO message (username, message, date) values (%(name)s, %(msg)s, %(date)s)'
        self.db_connector.save(query, params)
        LOGGER.info('[Storage] message {} saved in database'.format(params['msg']))

    def get_messages(self):
        query = 'SELECT * FROM message LIMIT 50'
        messages = self.db_connector.query(query, {})
        print(messages)

    def get_user_credentials(self, params):
        query = "SELECT password FROM participant WHERE username = %(username)s"
        return self.db_connector.query(query, params)

