import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options
import logging
from containers import Container

from handlers import ws_handler

from urls import urls
from settings import settings

define("port", default=9091, help="run on the given port", type=int)

LOGGER = logging.getLogger(__name__)


class Application(tornado.web.Application):

    def __init__(self):
        tornado.web.Application.__init__(self, urls, **settings)


def main():
    container = Container()
    container.config.from_yaml('config/config.yml')
    container.wire(modules=[ws_handler])

    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)

    LOGGER.info('[server.main] Starting server on http://127.0.0.1:%s', options.port)

    try:
        LOGGER.info("\n[server.main] Server Started.\n")

        tornado.ioloop.IOLoop.current().start()

    except KeyboardInterrupt:
        LOGGER.error('\n[server.main] EXCEPTION KEYBOARDINTERRUPT INITIATED\n')
        LOGGER.info("[server.main] Stopping Server....")
        LOGGER.info("\n[server.main] Server Stopped.")


if __name__ == "__main__":
    main()
