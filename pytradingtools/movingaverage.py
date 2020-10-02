from abc import ABCMeta, abstractmethod
from pytradingtools.utilities import RollingQueue

#==============================================#
    # In this file (in-order as they appear):
    #     MovingAverage(ABCMeta)
    #     SimpleMovingAverage(MovingAverage)
#==============================================#


#==============================================#
# START CLASSES
#==============================================#

class MovingAverage(metaclass=ABCMeta):
    '''
    Abstract base class for a moving average.

    Abstract Methods
    ----------------
    update(value)
        update the moving average with the next value.
    average
        the current average value of the moving average implementation.
    '''
    @abstractmethod
    def update(self, value):
        '''(Abstract) Update the moving average with value'''

    @property
    @abstractmethod
    def average(self):
        '''(Abstract) get the average value out of the moving average'''

class SimpleMovingAverage(MovingAverage):
    '''
        Averages the values of the given period.
    '''
    def __init__(self, period):
        '''
        period:
            the amount of data to use for the moving average value.
        '''
        if period < 1:
            raise ValueError("period must be greater than 0")

        self._recip_capacity = 1.0 / period
        self._average = 0.0
        self._queue = RollingQueue(period)

    def update(self, value):
        '''
        Update the moving average with the value given.

        Raises ValueError if value is non-numeric, or complex.
        '''
        if not isinstance(value, (int, float)):
            raise ValueError("non-numeric input given")

        # Get the value that is at the first to be removed when rolling:
        frontValue = self._queue.peek()

        if self._queue.isEmpty():
            self._average = value
            frontValue = value

        self._queue.enqueue(value)

        self._average -= frontValue * self._recip_capacity
        self._average += value * self._recip_capacity

    @property
    def average(self):
        '''Get the last average value of the SMA'''
        return self._average

    @property
    def period(self):
        '''Get the period of the SMA'''
        return self._queue.capacity
