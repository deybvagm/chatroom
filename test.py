import unittest
from utils import request_stock, build_message, extract_info_from_message, get_stock_code, get_destinate
from handlers.chat_participant import ChatParticipant
from config.config import Config
import csv
from unittest.mock import patch

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
            'some_info': 'test',
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
        def my_function(body):
            print(body)
            return body

        class MessageBrokerTest:
            def __init__(self, participant, params):
                self.participant = participant
                self.params = params

            def start(self):
                print('starting')

        message = '{"name": "jaz", "participants": 5, "msg_type": "public", "msg": "/stock", "stage": "msg"}'
        config = Config()

        with patch.object(ChatParticipant, 'handle_queue_event') as mock:
            client = ChatParticipant('jaz', message_cb=my_function, message_broker=MessageBrokerTest, config=config)
            client.handle_queue_event(message)
        mock.assert_called_once_with(message)


if __name__ == '__main__':
    unittest.main()



