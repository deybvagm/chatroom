from tornado.ioloop import IOLoop
from rabbitmq.pubsub import RabbitmqClient
from utils import request_stock
import json

import logging
LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, config, api_url, bot_name):
        LOGGER.info('[BotHandler] initiating bot')
        self.api_url = api_url
        self.rabbit_client = RabbitmqClient(self, config)
        self.rabbit_client.start()
        self._bot_name = bot_name
        IOLoop.current().start()

    def handle_queue_event(self, body):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        data = json.loads(body)
        stock_code = data['msg'].split('=')[1]
        response = request_stock(self.api_url, stock_code)
        data['msg'] = response
        data['name'] = self._bot_name

        routing_key = 'public'  # self.get_routing_key(msg['msg'])
        msg = json.dumps(data, ensure_ascii=False)
        self.rabbit_client.publish(msg, routing_key, app_id=self._bot_name)
