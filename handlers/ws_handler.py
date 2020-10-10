from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.escape import json_decode
from sockjs.tornado import SockJSConnection
import logging
import json

from rabbitmq.pubsub import RabbitmqClient
from config.config import Config
from utils import build_leaving_message, get_destinate

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
        self.api_command = config.api_command

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
        self.update_info(username=msg['name'], n_users=msg['participants'])
        receiver = self.get_destinate(msg['msg'])
        msg = json.dumps(msg, ensure_ascii=False)
        LOGGER.info('[ChatroomWSHandler] Publishing the received message to RabbitMQ: %s ' % msg)
        self.rabbit_client.publish(msg, receiver, app_id=self._username)

    def on_close(self):
        """
        This method is called when a websocket/sockjs connection is closed.

        :param      self  The object

        :return:     Doesn't return anything, except a confirmation of closed connection back to web app.
        """

        LOGGER.info('[ChatroomWSHandler] Websocket conneciton close event %s ' % self)

        user = self._username
        routing_key = self.get_destinate('')
        msg = build_leaving_message(user, routing_key, len(websocketParticipants))
        self.rabbit_client.publish(msg, routing_key, app_id=self._username)
        websocketParticipants.remove(self)
        LOGGER.info('[ChatroomWSHandler] Websocket connection closed')

    def handle_queue_event(self, body):
        json_decoded_body = json.loads(body)
        stage = json_decoded_body['stage']
        if stage == 'stop':
            LOGGER.warning('[ChatroomWSHandler] skipping sending message to websocket since webscoket is closed.')
            self.rabbit_client.stop()
        else:
            LOGGER.info('[ChatroomWSHandler] sending the message to corresponsding websoket')
            self.send(body)

    def update_info(self, username, n_users):
        self._username = username
        self._n_users = n_users

    def get_destinate(self, text):
        return get_destinate(text) if text.startswith(self.api_command) else None
