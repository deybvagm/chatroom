import uuid


class Config:
    def __init__(self, host='localhost', port=5672, exchange='chatexchange', exchange_type='topic',
                 binding_key='public', routing_key='public', bot_routing_key='/stock'):

        self.host = host
        self.queue = 'queue' + str(uuid.uuid4())
        self.port = port
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.binding_key = binding_key
        self.routing_key = routing_key
        self.bot_routing_key = bot_routing_key
