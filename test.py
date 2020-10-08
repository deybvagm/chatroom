import unittest
from utils import request_stock, build_message
import csv

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



if __name__ == '__main__':
    unittest.main()



