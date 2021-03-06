import unittest
# pylint: disable=line-too-long
from pytradingtools.movingaverage import MovingAverage, SimpleMovingAverage, ExponentialMovingAverage, SmoothedMovingAverage

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
        self.assertRaises(ValueError, SimpleMovingAverage, 1.5)

        p = 5
        sma = SimpleMovingAverage(p)

        self.assertEqual(sma.period, p)
        self.assertEqual(sma.average, 0.0)

    def test_average(self):
        '''Test the average after insertions:'''
        sma = SimpleMovingAverage(5)

        avg = 3.1415
        sma.update(avg)

        # Test first inserted value becomes the average:
        self.assertAlmostEqual(avg, sma.average)
        # Test value remains stable:
        for _ in range(0, 1000):
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

class TestExponentialMovingAverage(unittest.TestCase):
    '''Test Cases for EMA'''
    def test_base(self):
        '''Test that EMA inherits MovingAverage:'''
        # pylint: disable=unidiomatic-typecheck
        self.assertTrue(type(ExponentialMovingAverage.__base__) == type(MovingAverage))

    def test_initialization(self):
        '''Test initialization of EMA'''
        self.assertRaises(ValueError, ExponentialMovingAverage, 0)
        self.assertRaises(ValueError, ExponentialMovingAverage, -1)
        self.assertRaises(ValueError, ExponentialMovingAverage, 1.5)
        self.assertRaises(ValueError, ExponentialMovingAverage, 1, 0.9999)
        self.assertRaises(ValueError, ExponentialMovingAverage, 1, -1.0)
        self.assertRaises(ValueError, ExponentialMovingAverage, 1, 1j)

        p = 5
        ema = ExponentialMovingAverage(p)

        self.assertEqual(ema.period, p)
        self.assertEqual(ema.smoothing, 2.0)
        self.assertEqual(ema.average, 0.0)

    def test_average(self):
        '''Test the average value of the ema'''
        p = 5
        ema = ExponentialMovingAverage(p)

        avg = 3.1415
        ema.update(avg)
        # Test that the first insertion becomes the average:
        self.assertAlmostEqual(ema.average, avg)
        # Test value remains stable:
        for _ in range(0, 1000):
            ema.update(avg)
            self.assertAlmostEqual(avg, ema.average)

        p = 9
        ema = ExponentialMovingAverage(p, 2.0)

        # Test the value over a set of data:
        data = [22.81, 23.09, 22.91,
        23.23, 22.83, 23.05,
        23.02, 23.29, 23.41,
        23.49, 24.6, 24.63,
        24.51, 23.73]

        expected = [22.81, 22.84111,
        22.85222, 22.89889, 22.90111,
        22.92778, 22.95111, 23.00444,
        23.07111, 23.15489, 23.44391,
        23.68113, 23.8469, 23.82352]

        #pylint: disable=consider-using-enumerate
        for i in range(0, len(data)):
            ema.update(data[i])
            actual = round(ema.average, 5)
            self.assertAlmostEqual(actual, expected[i])

class TestSmoothedMovingAverage(unittest.TestCase):
    '''Test cases for SMMA'''
    def test_initialization(self):
        '''Test SMMA initialization'''
        self.assertRaises(ValueError, SmoothedMovingAverage, 0)
        self.assertRaises(ValueError, SmoothedMovingAverage, -1)
        self.assertRaises(ValueError, SmoothedMovingAverage, 1.5)
        self.assertRaises(ValueError, SmoothedMovingAverage, 1j)

        p = 5
        smma = SmoothedMovingAverage(p)

        self.assertEqual(smma.period, p)
        self.assertEqual(smma.smoothing, 1.0)
        self.assertEqual(smma.average, 0.0)
