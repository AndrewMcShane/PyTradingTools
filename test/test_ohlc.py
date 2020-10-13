import unittest
import os
from pytradingtools.ohlc import OhlcData, OhlcFileReader

# Helper for getting the current directory.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class TestOhlcData(unittest.TestCase):
    '''Tests for the OhlcData dataclass'''
    def test_initialization(self):
        '''Tests OhlcData initialization'''
        data = OhlcData(None, 100, 110, 90, 95, 95.5, 12345)

        self.assertAlmostEqual(data.open_price, 100)
        self.assertAlmostEqual(data.high_price, 110)
        self.assertAlmostEqual(data.low_price, 90)
        self.assertAlmostEqual(data.close_price, 95)
        self.assertAlmostEqual(data.adj_close_price, 95.5)
        self.assertAlmostEqual(data.volume,  12345)

class TestOhlcFileReader(unittest.TestCase):
    '''Tests for the OhlcFileReader class'''
    def test_improper_setup(self):
        '''
        Tests the file reader catching improper setup
            Expects a file without a adj_close column, but gets one.
            Expects a file without volume column, but gets one.
        '''
        data_path = os.path.join(THIS_DIR, 'test_ohlc_files/data_headers.csv')

        self.assertRaises(ValueError, OhlcFileReader, data_path, 1, ",", hasAdjClose=False)
        self.assertRaises(ValueError, OhlcFileReader, data_path, 1, ",", hasVolume=False)

    def test_data_headers(self):
        '''Test the file reader on basic data'''
        # Get the correct .csv file:
        data_path = os.path.join(THIS_DIR, 'test_ohlc_files/data_headers.csv')

        oReader = OhlcFileReader(data_path, 1, ",")

        olst = oReader.getData()
        self.assertEqual(len(olst), 10)
        # Test correct data order:
        ohlc01 = olst[0]
        self.assertAlmostEqual(ohlc01.open_price, 167.199997)
        self.assertAlmostEqual(ohlc01.high_price, 167.199997)
        self.assertAlmostEqual(ohlc01.low_price, 165.190002)
        self.assertAlmostEqual(ohlc01.close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.adj_close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.volume, 67820000)

    def test_data_no_headers(self):
        '''Test the file reader on a file without column headers'''
        data_path = os.path.join(THIS_DIR, 'test_ohlc_files/data_no_headers.csv')

        oReader = OhlcFileReader(data_path, 0, ",")

        olst = oReader.getData()
        self.assertEqual(len(olst), 10)
        # Test correct data order:
        ohlc01 = olst[0]
        self.assertAlmostEqual(ohlc01.open_price, 167.199997)
        self.assertAlmostEqual(ohlc01.high_price, 167.199997)
        self.assertAlmostEqual(ohlc01.low_price, 165.190002)
        self.assertAlmostEqual(ohlc01.close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.adj_close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.volume, 67820000)

    def test_data_headers_no_adj(self):
        '''Test the file reader on a file without an adjusted close column'''
        data_path = os.path.join(THIS_DIR, 'test_ohlc_files/data_headers_no_adj.csv')

        oReader = OhlcFileReader(file=data_path, ignoreLines=1, delimiter=",", hasAdjClose=False)

        olst = oReader.getData()
        self.assertEqual(len(olst), 10)
        # Test correct data order:
        ohlc01 = olst[0]
        self.assertAlmostEqual(ohlc01.open_price, 167.199997)
        self.assertAlmostEqual(ohlc01.high_price, 167.199997)
        self.assertAlmostEqual(ohlc01.low_price, 165.190002)
        self.assertAlmostEqual(ohlc01.close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.adj_close_price, 0)
        self.assertAlmostEqual(ohlc01.volume, 67820000)

    def test_data_headers_no_adj_vol(self):
        '''Test file reader on a source without adj close or volume columns'''
        data_path = os.path.join(THIS_DIR, 'test_ohlc_files/data_headers_no_adj_vol.csv')

        oReader = OhlcFileReader(
            file=data_path,
            ignoreLines=1,
            delimiter=",",
            hasAdjClose=False,
            hasVolume=False
            )

        olst = oReader.getData()
        self.assertEqual(len(olst), 10)
        # Test correct data order:
        ohlc01 = olst[0]
        self.assertAlmostEqual(ohlc01.open_price, 167.199997)
        self.assertAlmostEqual(ohlc01.high_price, 167.199997)
        self.assertAlmostEqual(ohlc01.low_price, 165.190002)
        self.assertAlmostEqual(ohlc01.close_price, 165.369995)
        self.assertAlmostEqual(ohlc01.adj_close_price, 0)
        self.assertAlmostEqual(ohlc01.volume, 0)
