from collections import deque
from math import sqrt
#==============================================#
#
#       In this file (in-order as they appear):
#           RollingQueue
#           RunningStats
#           RollingStats
#           RollingSum
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class RollingQueue:
    '''
    A fixed-size queue structure that automatically

    removes the first element from the queue when at capacity.

    Rolling Queues can be iterated and imlpement an __iter__ method.

    Properties
    ----------
    capacity:
        the max size of the queue

    size:
        the current size of the queue

    Methods
    -------
    isEmpty():
        returns if the queue is empty or not.

    atCapacity():
        returns if the queue is at capacity or not.

    peek():
        returns the element at the front of the queue, or None if empty.

    enqueue(value : object):
        adds an object into the queue. If at capacity, return the removed element, otherwise None.

    dequeue() raises ValueError:
        remove the first element from the rolling queue. Raises ValueError if empty.

    __iter__():
        returns an iterable of the rolling queue data

    Protected
    ---------
    _capacity : int
        maximum size of the rolling queue

    _size : int
        current size of the queue

    data: list
        underlying data  of the queue

    '''
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be greater than 0.")
        # Read only intention.
        self._capacity = capacity
        self._size = 0

        self.data = deque()

    def __iter__(self):
        return iter(self.data)

    def isEmpty(self):
        '''returns True if the rolling queue contains no elements'''
        return self._size == 0

    def atCapacity(self):
        '''returns True if the rolling queue is at capacity and will roll off old values'''
        return self.size == self._capacity

    def peek(self):
        '''Return the first element in the queue, otherwise None.'''
        if not self.isEmpty():
            return self.data[0]
        else:
            return None

    def enqueue(self, value):
        '''Enqueues an object to the list. If at capacity, returns the removed object, else None.'''
        removed = None
        if self._size == self._capacity:
            removed = self.data.popleft()
        else:
            self._size += 1

        self.data.append(value)

        return removed

    def dequeue(self):
        '''Remove the element in front of the queue and return it. Raises ValueError if empty.'''
        if self.isEmpty():
            raise ValueError("the queue is empty.")
        else:
            self._size -= 1
            return self.data.popleft()
    @property
    def capacity(self):
        '''The capacity of the rolling queue. Read-only'''
        return self._capacity

    @property
    def size(self):
        '''The current size of the rolling queue. Read-only'''
        return self._size

class RunningStats:
    '''
    An online algorithm to caclulate statistics in a running fashion.
    '''
    def __init__(self):
        self._n = 0
        self._oldMean = 0.0
        self._newMean = 0.0
        # Variance Sum:
        self._oldSum = 0.0
        self._newSum = 0.0

    def clear(self):
        '''Reset the rolling statistic'''
        self._n = 0

    def push(self, value):
        '''Adds a value to the running data set'''
        self._n += 1
        if self._n == 1:
            self._oldMean = self._newMean = value
            self._oldSum = 0.0
        else:
            self._newMean = self._oldMean +  (value - self._oldMean) / self._n
            self._newSum = self._oldSum + (value - self._oldMean) * (value - self._newMean)

            # Prep the next iteration:
            self._oldMean = self._newMean
            self._oldSum = self._newSum

    @property
    def mean(self):
        '''Return the mean value of the data set.'''
        return self._newMean if self._n > 0 else 0.0

    @property
    def variance(self):
        '''
        Return the variance of the data set

        Uses Bessel's Correction of `variance-sum / (n - 1)`
        '''
        return self._newSum / (self._n - 1) if self._n > 1 else 0.0

    @property
    def stddev(self):
        '''
        Return the standard deviation of the data set

        Standard deviation is the square root of the variance.
        When possible, prefer to use variance.
        '''
        return sqrt(self.variance)

class RollingStats:
    '''
    This is a rolling implementation of Donald Knuth's algorithm, using
    Welford's method.

    Notice:
        unitl there is enough data to begin rolling (n >= period)
        where data size = n, the results from this will be very innacurate.
        To check accuracy, use `RollingStats.isaccurate`
    '''
    def __init__(self, period):
        '''
        period: `int` The number of days to  trace the stats back,
        also referred to as the 'window'.
        '''
        self._queue = RollingQueue(period)
        # Variance Sum:
        self._varS = 0.0
        self._mean = 0.0
        # Cache the recip to avoid division:
        self._recip_size = 1 / period
        # Cache the recip with Bessel's correction:
        self._bessel_recip = 1 / (period - 1)

    def push(self, value):
        '''
        Push a value into the rolling data set.

        value : `int,float`
        '''
        # Calculate the mean:
        frontVal = self._queue.peek()

        if self._queue.isEmpty():
            self._mean = value
            frontVal = value

        self._queue.enqueue(value)
        new_mean = old_mean = self._mean

        new_mean -= frontVal * self._recip_size
        new_mean += value * self._recip_size

        self._varS += (value + frontVal - old_mean - new_mean) * (value - frontVal)

        # Next iteration setup:
        self._mean = new_mean

    @property
    def mean(self):
        '''
        The Mean of the rolling data.
        '''
        return self._mean

    @property
    def variance(self):
        '''
        The Variance of the rolling data.
        '''
        return self._varS * self._bessel_recip

    @property
    def stddev(self):
        '''The Standard Deviation of the rolling data'''
        return sqrt(self.variance)

    @property
    def isaccurate(self):
        '''
        `bool`
        if false, the data window has not been filled yet,
        and will not be fully accurate.

        In graphing and calculations, consider using `None`
        in place of the inaccurate values. i.e.,

            if not rstats.isaccurate:
                return None
            else:
                return rstats.variance

        Alternatively, you can use `RunningStats` until the data has become accurate
        to get accurate sample deviaitons
        '''
        return self._queue.atCapacity()

class RollingSum:
    '''
    Calculates the sum of the last n-periods on a rolling basis.
    '''
    def __init__(self, period):
        self._sum = 0.0
        self._data = RollingQueue(period)

    def update(self, value):
        '''
        value: `float` the new value to add to the rolling sum.
        '''
        rem = self._data.enqueue(value)
        if rem is not None:
            self._sum -= rem
        self._sum += value

    @property
    def sum(self):
        '''Returns the current value of the rolling sum'''
        return self._sum
