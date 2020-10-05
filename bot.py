from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

from pubsub import RabbitmqClient
from config import Config

import logging
logging.basicConfig(level=logging.INFO)

define("host", default='localhost', help="host for the Rabbitmq server", type=str)
define("port", default=5672, help="port for Rabbitmq", type=int)
define("binding_key", default='stock', help="binding_key for Rabbitmq", type=str)
define("routing_key", default='public.*', help="routing key for Rabbitmq", type=str)

LOGGER = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, config):
        LOGGER.info('[BotHandler] initiating bot')
        self.rabbit_client = RabbitmqClient(self, config)
        self.rabbit_client.start()
        IOLoop.current().start()

    def handle_queue_event(self, body):
        LOGGER.info('[BotHandler] Bot detected a request for stock')
        a = {"name": "bot", "stage": "msg", "msg": "my data", "msg_type": "public", "clientid": None}
        self.rabbit_client.publish(a)


if __name__ == "__main__":
    parse_command_line()
    config = Config(
        host=options.host, port=options.port, binding_key=options.binding_key, routing_key=options.routing_key
    )
    LOGGER.info("\n[BotHandler] Starting bot.\n")
    bot = BotHandler(config)


