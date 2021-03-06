from typing import Any

from tornado import httputil
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from sockjs.tornado import SockJSConnection
from tornado.escape import json_decode
import logging
import json

from dependency_injector.wiring import Provide
from containers import Container

LOGGER = logging.getLogger(__name__)

# Main threads ioloop, not to be confused with current thread's ioloop
# which is ioloop.IOLoop.current()
ioloop = IOLoop.instance()


# Handles the general HTTP connections
class IndexHandler(RequestHandler):
    """This handler is a basic regular HTTP handler to serve the chatroom page.

    """

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest,
                 auth_handler=Provide[Container.auth_handler], **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.auth_handler = auth_handler

    def get(self):
        """
        This method is called when a client does a simple GET request,
        all other HTTP requests like POST, PUT, DELETE, etc are ignored.

        :return: Returns the rendered main requested page, in this case its the chat page, index.html
        """

        LOGGER.info('[IndexHandler] HTTP connection opened')

        self.render('index.html')

        LOGGER.info('[IndexHandler] index.html served')

    def post(self):
        user_info = json_decode(self.request.body)
        nickname = user_info['user']
        unchecked_pass = user_info['pass']
        LOGGER.info('[IndexHandler] request for login received for username {}'.format(nickname))
        if self.auth_handler.validate_authentication(nickname, unchecked_pass):
            auth_response = 'ok'
        else:
            LOGGER.warning('Invalid credentials for username {}'.format(nickname))
            auth_response = 'error'
        self.write(json.dumps({'msg': auth_response}))


# no. of websocket connections
websocketParticipants = set()


# Handler for Websocket Connections or Sockjs Connections
class ChatroomWSHandler(SockJSConnection):
    """ Websocket Handler implementing the sockjs Connection Class which will
    handle the websocket/sockjs connections.
    """
    def __init__(self, session, chat_participant=Provide[Container.chat_participant]):
        super().__init__(session)
        self.chat_participant = chat_participant

    def on_open(self, info):
        """
        This method is called when a websocket/sockjs connection is opened for the first time.

        :param      self  The object
        :param      info  The information

        :return:    It returns the websocket object

        """

        LOGGER.info('[ChatroomWSHandler] Websocket connection opened: %s ' % self)
        websocketParticipants.add(self)
        self.chat_participant.setup(self.send_message, username=None)

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
