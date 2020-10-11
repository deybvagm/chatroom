from tornado.ioloop import IOLoop
from utils import request_stock, get_stock_code
import json

import logging
LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, api_url, bot_name, config, message_broker):
        LOGGER.info('[BotHandler] initiating bot')
        self.api_url = api_url
        self.rabbit_client = message_broker(config)
        self.rabbit_client.start(self.handle_queue_event)
        self._bot_name = bot_name
        IOLoop.current().start()

    def handle_queue_event(self, body):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        data = json.loads(body)
        stock_code = get_stock_code(data['msg'])
        response = request_stock(self.api_url, stock_code)
        data['msg'] = response
        data['name'] = self._bot_name

        msg = json.dumps(data, ensure_ascii=False)
        self.rabbit_client.publish(msg, routing_key=None, app_id=self._bot_name)
