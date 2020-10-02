import unittest
from pytradingtools.movingaverage import MovingAverage, SimpleMovingAverage

class TestMovingAverage(unittest.TestCase):
    '''Test Cases for the Moving Average Base Class'''
    def test_initialization(self):
        '''Test that a moving average cannot be instanced:'''
        self.assertRaises(TypeError, MovingAverage)

class TestSimpleMovingAverage(unittest.TestCase):
    '''Test Cases for the SMA'''
    def test_base(self):
        '''Test that SMA inherits MovingAverage:'''
        # pylint: disable=unidiomatic-typecheck
        self.assertTrue(type(SimpleMovingAverage.__base__) == type(MovingAverage))

    def test_initialization(self):
        '''Test initialization of SMA:'''
        self.assertRaises(ValueError, SimpleMovingAverage, 0)
        self.assertRaises(ValueError, SimpleMovingAverage, -1)

        p = 5
        recip_p = 1.0 / p
        sma = SimpleMovingAverage(p)

        self.assertEqual(sma.period, p)
        self.assertEqual(sma.average, 0.0)
        # pylint: disable=protected-access
        self.assertAlmostEqual(sma._recip_capacity, recip_p)

    def test_average(self):
        '''Test the average after insertions:'''
        sma = SimpleMovingAverage(5)

        avg = 3.1415
        sma.update(avg)

        # Test first inserted value becomes the average:
        self.assertAlmostEqual(avg, sma.average)
        # Test value remains stable:
        for i in range(0, 1000):
            sma.update(avg)
            self.assertAlmostEqual(avg, sma.average)

        p = 5
        recip_p = 1.0 / p
        sma = SimpleMovingAverage(p)
        expected = float(0.0)
        # Test value over changing data:
        for i in range(0, 1000):

            sma.update(i)

            if i - p <= 0:
                expected += i * recip_p
            else:
                expected -= (i - p) * recip_p
                expected += i * recip_p

            self.assertAlmostEqual(expected, sma.average)
