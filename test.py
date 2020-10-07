import unittest
from utils import request_stock

class TestSum(unittest.TestCase):

    def test_sum(self):
        url = 'https://stooq.com/q/l/?s=STOCK_CODE&f=sd2t2ohlcv&h&e=csv'
        text = request_stock(url, stock_code='aapl.us')
        self.assertTrue(text.startswith('AAPL.US quote is $')), 'Should start with AAPL.US'


if __name__ == '__main__':
    unittest.main()



