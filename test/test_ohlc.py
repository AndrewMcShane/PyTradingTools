import unittest
from pytradingtools.ohlc import OhlcData

class TestOhlcData(unittest.TestCase):
    '''Tests for the OhlcData dataclass'''
    def test_initialization(self):
        '''Tests OhlcData initialization'''
        data = OhlcData(None, 100, 110, 90, 95, 12345)

        self.assertAlmostEqual(data.open_price, 100)
        self.assertAlmostEqual(data.high_price, 110)
        self.assertAlmostEqual(data.low_price, 90)
        self.assertAlmostEqual(data.close_price, 95)
        self.assertAlmostEqual(data.volume,  12345)
