from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from sockjs.tornado import SockJSConnection
from tornado.escape import json_decode
import logging

from handlers.chat_participant import ChatParticipant

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
        websocketParticipants.add(self)
        self.chat_participant = ChatParticipant(username=None, message_cb=self.send_message)

    def on_message(self, message):
        """
        This method is called when a message is received via the websocket/sockjs connection
        created initially.

        :param      self     The object
        :param      message  The message received via the connection.

        :return:     Returns the published message back to all other subscribers.

        """

        LOGGER.info('[ChatroomWSHandler] message received on Websocket: %s ' % self)
        message = json_decode(message)
        self.chat_participant.notify(message, len(websocketParticipants))

    def on_close(self):
        """
        This method is called when a websocket/sockjs connection is closed.

        :param      self  The object

        :return:     Doesn't return anything, except a confirmation of closed connection back to web app.
        """

        LOGGER.info('[ChatroomWSHandler] Websocket conneciton close event %s ' % self)
        self.chat_participant.handle_closed_connection(len(websocketParticipants))
        websocketParticipants.remove(self)
        LOGGER.info('[ChatroomWSHandler] Websocket connection closed')

    def send_message(self, body):
        LOGGER.info('[ChatroomWSHandler] sending the message from websoket')
        self.send(body)
