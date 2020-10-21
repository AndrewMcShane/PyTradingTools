import unittest
import math
from pytradingtools.utilities import RollingQueue, RunningStats, RollingStats, RollingSum

class TestRollingQueue(unittest.TestCase):
    '''Tests for the rolling queue util'''
    def test_initialization(self):
        '''Tests creation of a rolling queue.'''
        self.assertRaises(ValueError, RollingQueue, 0)
        self.assertRaises(ValueError, RollingQueue, -1)

        q = RollingQueue(10)
        self.assertTrue(q.size == 0)
        self.assertTrue(q.capacity == 10)

    def test_empty_and_at_capacity(self):
        '''Tests the isEmpty and atCapacity methods.'''
        q = RollingQueue(1)
        self.assertTrue(q.isEmpty())
        self.assertFalse(q.atCapacity())

        q.enqueue(1)

        self.assertFalse(q.isEmpty())
        self.assertTrue(q.atCapacity())

    def test_peek(self):
        '''Tests the peek method return values'''
        q = RollingQueue(1)
        self.assertEqual(None, q.peek())

        value = "hello"
        q.enqueue(value)
        self.assertEqual(value, q.peek())

        q.dequeue()
        self.assertEqual(None, q.peek())

    def test_enqueue(self):
        '''Tests the enqueue method'''
        q = RollingQueue(1)

        inputVal = "hello"
        returnVal = q.enqueue(inputVal)
        self.assertEqual(None, returnVal)

        returnVal = q.enqueue("world")
        self.assertEqual(inputVal, returnVal)

    def test_dequeue(self):
        '''Tests the dequeue method:'''
        q = RollingQueue(2)

        A = "A"
        B = "B"

        self.assertRaises(ValueError, q.dequeue)

        q.enqueue(A)
        self.assertEqual(A, q.dequeue())

        q.enqueue(A)
        q.enqueue(B)
        self.assertEqual(A, q.dequeue())
        self.assertEqual(B, q.dequeue())
        self.assertRaises(ValueError, q.dequeue)

    def test_iter(self):
        '''Test the built-in iterable'''
        cap = 10
        q = RollingQueue(cap)

        for i in range(0, cap):
            q.enqueue(i)

        self.assertEqual(q.size, cap)
        self.assertTrue(q.atCapacity())

        expected = 0
        for value in q:
            self.assertEqual(value, expected)
            expected += 1

        self.assertEqual(cap, expected)

class TestRunningStats(unittest.TestCase):
    '''Tests the RunningStats class'''
    def test_running(self):
        '''Test the Running stats over simple use cases'''
        rs = RunningStats()

        data = [5, 6, 7, 8, 9, 10, 12, 6, 2]
        expectedMean= 65/9
        expectedVariance = 69.556/8
        expecteStdDev = math.sqrt(expectedVariance)

        for point in data:
            rs.push(point)

        self.assertAlmostEqual(rs.mean, expectedMean)
        self.assertAlmostEqual(rs.variance, expectedVariance, 3)
        self.assertAlmostEqual(rs.stddev, expecteStdDev, 3)

class TestRollingStats(unittest.TestCase):
    '''Tests the RollingStats class'''
    def test_rolling(self):
        '''Test the Rolling Stats over simple use-cases'''
        period = 5
        rs = RollingStats(period)

        data = [5, 6, 7, 8, 9]
        expM = 7
        expVar = 2.5
        expStd = math.sqrt(expVar)

        for point in data:
            rs.push(point)

        self.assertTrue(rs.isaccurate)
        self.assertAlmostEqual(rs.mean, expM)
        self.assertAlmostEqual(rs.variance, expVar, 3)
        self.assertAlmostEqual(rs.stddev, expStd, 3)

        # Test the data once it's rolled:
        rs.push(4)

        expM = 6.8
        expVar = 3.7
        expStd = math.sqrt(expVar)

        self.assertAlmostEqual(rs.mean, expM)
        self.assertAlmostEqual(rs.variance, expVar, 3)
        self.assertAlmostEqual(rs.stddev, expStd, 3)

class TestRollingSum(unittest.TestCase):
    '''Tests the RollingSum class'''
    def test_rolling(self):
        '''Test the RollingSum over simple use-cases'''
        period = 5
        rs = RollingSum(period)
        for i in range(0, period):
            rs.update(1)

        self.assertEqual(rs.sum, period)

        for i in range(0, 1000):
            rs.update(1)

        self.assertEqual(rs.sum, period)

        data = [1,2,3,4,5]
        for i in data:
            rs.update(i)

        expected = sum(data)
        self.assertEqual(rs.sum, expected)

        nplus = 6
        rs.update(nplus)
        expected -= data[0]
        expected += nplus

        self.assertEqual(rs.sum, expected)
