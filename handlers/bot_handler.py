from tornado.ioloop import IOLoop
from rabbitmq.pubsub import RabbitmqClient
from handlers.chat_participant import ChatParticipant
from utils import request_stock, get_stock_code
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

        self.chat_participant = ChatParticipant(bot_name, self.handle_queue_event)
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
