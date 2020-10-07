from tornado.options import define, options, parse_command_line
from config.config import Config
from handlers.bot_handler import BotHandler

define("host", default='localhost', help="host for the Rabbitmq server", type=str)
define("port", default=5672, help="port for Rabbitmq", type=int)
define("binding_key", default='/stock', help="binding_key for Rabbitmq", type=str)
define("routing_key", default='public', help="routing key for Rabbitmq", type=str)
define("api_url", default='https://stooq.com/q/l/?s=STOCK_CODE&f=sd2t2ohlcv&h&e=csv', help="api for stock", type=str)
define("bot", default='bot', help="name for the bot", type=str)


if __name__ == "__main__":
    parse_command_line()
    config = Config(
        host=options.host, port=options.port, binding_key=options.binding_key, routing_key=options.routing_key
    )
    bot = BotHandler(config, options.api_url, bot_name=options.bot)


