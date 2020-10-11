from tornado.ioloop import IOLoop
from utils import request_stock, get_stock_code
import json

import logging
LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, config, message_broker):
        LOGGER.info('[BotHandler] initiating bot')
        self.api_url = config['api_url']
        self.message_broker = message_broker
        self._bot_name = config['name']

    def start(self):
        self.message_broker.start(self.handle_queue_event)
        IOLoop.current().start()

    def handle_queue_event(self, body):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        data = json.loads(body)
        stock_code = get_stock_code(data['msg'])
        response = request_stock(self.api_url, stock_code)
        data['msg'] = response
        data['name'] = self._bot_name

        msg = json.dumps(data, ensure_ascii=False)
        self.message_broker.publish(msg, routing_key=None, app_id=self._bot_name)
