import psycopg2

import logging
LOGGER = logging.getLogger(__name__)


class DBConnector:

    def __init__(self, config):
        try:
            self.connection = psycopg2.connect(
                host=config['host'],
                database=config['name'],
                user=config['user'],
                password=config['password']
            )
            self.db_cur = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            LOGGER.error('[DBConnector] An error occurred connecting to to database', error)

    def query(self, query, params):
        self.db_cur.execute(query, params)
        result = self.db_cur.fetchone()
        return result

    def insert(self, query, params):
        self.db_cur.execute(query, params)
        self.connection.commit()

    def __del__(self):
        self.db_cur.close()
        self.connection.close()





