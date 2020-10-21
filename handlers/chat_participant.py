from datetime import datetime
import json
import logging

from utils import build_leaving_message, extract_info_from_message

LOGGER = logging.getLogger(__name__)


class ChatParticipant:
    def __init__(self, message_broker, config, storage):
        self._username = None
        self._nusers = 0
        self.message_cb = None
        self._api_command = config['api_command']
        self.message_broker = message_broker
        self.storage = storage
        self.message_broker.start(self.handle_queue_event)

    def setup(self, message_cb, username):
        self._username = username
        self.message_cb = message_cb

    def update_info(self, username, n_users):
        if self._username is None:
            self._username = username
        self._nusers = n_users

    def get_receiver(self, command):
        return command if command.startswith(self._api_command) else None

    def notify(self, message, n_users):
        msg, username, command = extract_info_from_message(message, n_users)
        receiver = self.get_receiver(command)
        self.update_info(username=username, n_users=n_users)
        LOGGER.info('[ChatParticipant] Publishing the received message to RabbitMQ: %s ' % msg)
        self.message_broker.publish(msg, receiver, app_id=self._username)

    def handle_queue_event(self, body):
        json_decoded_body = json.loads(body)
        stage = json_decoded_body['stage']
        if stage == 'stop':
            LOGGER.warning('[ChatParticipant] skipping sending message to websocket since webscoket is closed.')
            self.message_broker.stop()
        else:
            LOGGER.info('[ChatParticipant] sending the message to corresponding web socket')
            json_decoded_body['date'] = datetime.now()
            self.storage.save_message(json_decoded_body)
            self.message_cb(body)

    def handle_closed_connection(self, n):
        user = self._username
        routing_key = self.get_receiver('')
        msg = build_leaving_message(user, routing_key, n)
        LOGGER.info('[ChatParticipant] closing connection')
        self.message_broker.publish(msg, routing_key, app_id=self._username)



