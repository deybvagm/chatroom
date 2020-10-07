from tornado.ioloop import IOLoop
from tornado.escape import json_decode
from rabbitmq.pubsub import RabbitmqClient
from utils import request_stock

import logging
LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, config, api_url, bot_name):
        LOGGER.info('[BotHandler] initiating bot')
        self.api_url = api_url
        self.rabbit_client = RabbitmqClient(self, config, username=bot_name)
        self.rabbit_client.start()
        IOLoop.current().start()

    def handle_queue_event(self, data):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        data = json_decode(data)
        stock_code = data['msg'].split('=')[1]
        response = request_stock(self.api_url, stock_code)
        data['msg'] = response
        data['name'] = self.rabbit_client.get_username()
        self.rabbit_client.publish(data)