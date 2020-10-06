from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.escape import json_decode

from pubsub import RabbitmqClient
from config import Config
from utils import request_stock

import logging
logging.basicConfig(level=logging.INFO)

define("host", default='localhost', help="host for the Rabbitmq server", type=str)
define("port", default=5672, help="port for Rabbitmq", type=int)
define("binding_key", default='/stock', help="binding_key for Rabbitmq", type=str)
define("routing_key", default='public.*', help="routing key for Rabbitmq", type=str)
define("api_url", default='https://stooq.com/q/l/?s=STOCK_CODE&f=sd2t2ohlcv&h&e=csv', help="api for stock", type=str)

LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, config):
        LOGGER.info('[BotHandler] initiating bot')
        self.rabbit_client = RabbitmqClient(self, config)
        self.rabbit_client.start()
        IOLoop.current().start()

    def handle_queue_event(self, data):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        data = json_decode(data)
        stock_code = data['msg'].split('=')[1]
        url = self.rabbit_client.get_config().api_url
        response = request_stock(url, stock_code)
        data['name'] = 'bot'
        data['msg'] = response
        self.rabbit_client.publish(data)


if __name__ == "__main__":
    parse_command_line()
    config = Config(
        host=options.host, port=options.port, binding_key=options.binding_key,
        routing_key=options.routing_key, api_url=options.api_url
    )
    LOGGER.info("\n[BotHandler] Starting bot.\n")
    bot = BotHandler(config)


