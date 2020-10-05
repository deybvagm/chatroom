import uuid
class RabbitMqConfig:
    def __init__(self, host='localhost', queue='chatroom1', port=5672, exchange='chatexchange',
                 exchange_type='topic', binding_key='public.*'):

        """ Server initialization   """

        self.host = host
        self.queue = 'queue' + str(uuid.uuid4())
        self.port = port
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.binding_key = binding_key
