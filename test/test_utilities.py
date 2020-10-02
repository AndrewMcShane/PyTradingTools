import unittest
from pytradingtools.utilities import RollingQueue

class TestRollingQueue(unittest.TestCase):
    def test_initialization(self):
        # Tests creation of a rolling queue.
        self.assertRaises(ValueError, RollingQueue, 0)
        self.assertRaises(ValueError, RollingQueue, -1)

        q = RollingQueue(10)
        self.assertTrue(q.size == 0)
        self.assertTrue(q.capacity == 10)

    def test_empty_and_at_capacity(self):
        # Tests the isEmpty and atCapacity methods.
        q = RollingQueue(1)
        self.assertTrue(q.isEmpty())
        self.assertFalse(q.atCapacity())

        q.enqueue(1)

        self.assertFalse(q.isEmpty())
        self.assertTrue(q.atCapacity())

    def test_peek(self):
        # Tests the peek method return values
        q = RollingQueue(1)
        self.assertEqual(None, q.peek())

        value = "hello"
        q.enqueue(value)
        self.assertEqual(value, q.peek())

        q.dequeue()
        self.assertEqual(None, q.peek())

    def test_enqueue(self):
        # Tests the enqueue method
        q = RollingQueue(1)

        inputVal = "hello"
        returnVal = q.enqueue(inputVal)
        self.assertEqual(None, returnVal)

        returnVal = q.enqueue("world")
        self.assertEqual(inputVal, returnVal)

    def test_dequeue(self):
        # Tests the dequeue method:
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
        # Test the built-in iterable
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
