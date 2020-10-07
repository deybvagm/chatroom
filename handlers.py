from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.escape import json_decode
from sockjs.tornado import SockJSConnection
import logging

from pubsub import RabbitmqClient
from config import Config
from utils import build_leaving_message

LOGGER = logging.getLogger(__name__)

# Main threads ioloop, not to be confused with current thread's ioloop
# which is ioloop.IOLoop.current()
ioloop = IOLoop.instance()


# Handles the general HTTP connections
class IndexHandler(RequestHandler):
    """This handler is a basic regular HTTP handler to serve the chatroom page.

    """

    def get(self):
        """
        This method is called when a client does a simple GET request,
        all other HTTP requests like POST, PUT, DELETE, etc are ignored.

        :return: Returns the rendered main requested page, in this case its the chat page, index.html
        """

        LOGGER.info('[IndexHandler] HTTP connection opened')

        self.render('index.html')

        LOGGER.info('[IndexHandler] index.html served')


# no. of websocket connections
websocketParticipants = set()


# Handler for Websocket Connections or Sockjs Connections
class ChatroomWSHandler(SockJSConnection):
    """ Websocket Handler implementing the sockjs Connection Class which will
    handle the websocket/sockjs connections.
    """

    def on_open(self, info):
        """
        This method is called when a websocket/sockjs connection is opened for the first time.

        :param      self  The object
        :param      info  The information

        :return:    It returns the websocket object

        """

        LOGGER.info('[ChatroomWSHandler] Websocket connection opened: %s ' % self)

        config = Config()
        self.rabbit_client = RabbitmqClient(self, config)
        websocketParticipants.add(self)
        self.rabbit_client.start()

    def on_message(self, message):
        """
        This method is called when a message is received via the websocket/sockjs connection
        created initially.

        :param      self     The object
        :param      message  The message received via the connection.

        :return:     Returns the published message back to all other subscribers.

        """

        LOGGER.info('[ChatroomWSHandler] message received on Websocket: %s ' % self)
        res = json_decode(message)
        msg = res['msg']
        msg['participants'] = len(websocketParticipants)
        LOGGER.info('[ChatroomWSHandler] Publishing the received message to RabbitMQ: %s ' % msg)
        self.rabbit_client.publish(msg)

    def on_close(self):
        """
        This method is called when a websocket/sockjs connection is closed.

        :param      self  The object

        :return:     Doesn't return anything, except a confirmation of closed connection back to web app.
        """

        LOGGER.info('[ChatroomWSHandler] Websocket conneciton close event %s ' % self)

        user = self.rabbit_client.get_username()
        routing_key = self.rabbit_client.get_routing_key('')
        msg = build_leaving_message(user, routing_key, len(websocketParticipants))
        self.rabbit_client.publish(msg)
        websocketParticipants.remove(self)
        LOGGER.info('[ChatroomWSHandler] Websocket connection closed')

    def handle_queue_event(self, body):
        self.send(body)
