import unittest
from unittest.mock import patch
from unittest.mock import Mock
from nacl import pwhash
import csv
import yaml

from utils import request_stock, build_message, extract_info_from_message, get_stock_code, get_destinate
from handlers.chat_participant import ChatParticipant
from handlers.bot_handler import BotHandler
from handlers.auth import AuthHandler
from handlers.storage import Storage
from rabbitmq.pubsub import RabbitmqClient


class TestApi(unittest.TestCase):

    def test_stock_api_response_with_aapl_stok_code(self):
        url = 'https://stooq.com/q/l/?s=STOCK_CODE&f=sd2t2ohlcv&h&e=csv'
        text = request_stock(url, stock_code='aapl.us')
        self.assertTrue(text.startswith('AAPL.US quote is $')), 'Should start with AAPL.US'

    def test_content_extraction_from_csv_file_and_build_message(self):
        with open('tests/aapl.us.csv') as csvfile:
            file_reader = csv.reader(csvfile)
            text = build_message(file_reader)
            self.assertEqual('AAPL.US quote is $114.305 per share', text), 'Text should be AAPL.US ...'

    def test_stock_code_extraction(self):
        text = '/stock=aapl.us'
        stock_code = get_stock_code(text)
        self.assertEqual(stock_code, 'aapl.us'), 'stock code should be aapl.us'

    def test_command_extraction(self):
        text = '/stock=aapl.us'
        command = get_destinate(text)
        self.assertEqual(command, '/stock'), 'stock code should be /stock'

    def test_info_extraction_from_message(self):
        message = {
            'some_info': 'tests',
            'msg': {
                'name': 'jaz',
                'participants': 5,
                'msg_type': 'public',
                'msg': '/stock'


            }
        }
        msg, user, command = extract_info_from_message(message, n_users=5)
        self.assertEqual(user, 'jaz'), 'user should be jaz'
        self.assertEqual(command, '/stock'), 'command should be /stock'
        self.assertEqual(msg, '{"name": "jaz", "participants": 5, "msg_type": "public", "msg": "/stock"}')

    def test_on_message_cb(self):

        class MyClass:
            @staticmethod
            def my_callback(data):
                pass

        message = '{"name": "jaz", "participants": 5, "msg_type": "public", "msg": "/stock", "stage": "msg"}'
        with open('tests/test_config.yml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        message_broker_mock = Mock(spec=RabbitmqClient)
        storage_mock = Mock(spec=Storage)
        with patch.object(MyClass, 'my_callback') as mock:
            mock.return_value.start.return_value = ''
            client = ChatParticipant(message_broker=message_broker_mock, config=config, storage=storage_mock)
            client.setup(MyClass.my_callback, username='user1')
            client.handle_queue_event(message)
        mock.assert_called_once_with(message)

    def test_notify_message(self):
        class MyClass:

            @staticmethod
            def my_callback():
                pass

        message = {
            "msg": {"name": "jaz", "participants": 5, "msg_type": "public", "msg": "/stock", "stage": "msg"}
        }
        expected_message = '{"name": "jaz", "participants": 6, "msg_type": "public", "msg": "/stock", "stage": "msg"}'
        with open('tests/test_config.yml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        mock_storage = Mock(spec=Storage)
        message_broker_mock = Mock(spec=RabbitmqClient)
        with patch.object(message_broker_mock, 'publish') as mock:
            client = ChatParticipant(message_broker=message_broker_mock, config=config, storage=mock_storage)
            client.setup(MyClass.my_callback, username='user1')
            client.notify(message, n_users=6)
        mock.assert_called_once_with(expected_message,  '/stock', app_id='user1')

    def test_bot_handler(self):
        message = '{"name": "jaz", "participants": 5, "msg_type": "public", "msg": "/stock=aapl.us", "stage": "msg"}'
        expected_message = '{"name": "bot", "participants": 5, "msg_type": "public", "msg": "AAPL.US quote is $'
        with open('tests/test_config_bot.yml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        message_broker_mock = Mock(spec=RabbitmqClient)
        with patch.object(message_broker_mock, 'publish') as mock:
            client = BotHandler(message_broker=message_broker_mock, config=config)
            client.handle_queue_event(message)
        mock.assert_called_once()
        msg = mock.call_args[0]
        self.assertTrue(msg[0].startswith(expected_message)), 'Should start wth correct message format'

    def test_authentication_failed_when_user_does_not_exist(self):
        username = 'user1'
        unchecked_password = '123'
        store_mock = Mock(spec=Storage)
        store_mock.get_user_credentials.return_value = None
        auth = AuthHandler(store_mock)
        response = auth.validate_authentication(username, unchecked_password)
        self.assertFalse(response)

    def test_authentication_success_when_user_and_pass_match(self):
        username = 'valid_user'
        unchecked_password = 'valid_password'
        hashed_pass = pwhash.argon2id.str(bytes('valid_password', 'utf-8'))
        decoded_pass = hashed_pass.decode("utf-8")
        store_mock = Mock(spec=Storage)
        store_mock.get_user_credentials.return_value = (decoded_pass,)
        auth = AuthHandler(store_mock)
        response = auth.validate_authentication(username, unchecked_password)
        self.assertTrue(response)

    def test_authentication_fail_when_user_and_pass_do_not_match(self):
        username = 'valid_user'
        unchecked_password = 'invalid_password'
        hashed_pass = pwhash.argon2id.str(bytes('valid_password', 'utf-8'))
        decoded_pass = hashed_pass.decode("utf-8")
        store_mock = Mock(spec=Storage)
        store_mock.get_user_credentials.return_value = (decoded_pass,)
        auth = AuthHandler(store_mock)
        response = auth.validate_authentication(username, unchecked_password)
        self.assertFalse(response)


if __name__ == '__main__':
    unittest.main()



