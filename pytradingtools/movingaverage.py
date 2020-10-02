from abc import ABCMeta, abstractmethod
from pytradingtools.utilities import RollingQueue

#==============================================#
    # In this file (in-order as they appear):
    #       MovingAverage(ABCMeta)
    #       SimpleMovingAverage(MovingAverage)
    #       ExponentialMovingAverage(MovingAverage)
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
        '''
        Update the moving average with the value given.

        Raises ValueError if value is non-numeric, or complex.
        '''

    @property
    @abstractmethod
    def average(self):
        '''(Abstract) get the average value out of the moving average'''

class SimpleMovingAverage(MovingAverage):
    '''
        Averages the values of the given period, giving equal weight to each day.
    '''
    def __init__(self, period):
        '''
        period:
            the amount of data to use for the moving average value.
        '''
        if not isinstance(period, int) and period < 1:
            raise ValueError("period must be an integer and greater than 0")

        self._recip_capacity = 1.0 / period
        self._average = 0.0
        self._queue = RollingQueue(period)

    def update(self, value):
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

class ExponentialMovingAverage(MovingAverage):
    '''
        Averages the values of a given period
        by a smoothing factor, placing more emphasis on new data.

        EMA formula:
            EMA = (VALUE - EMAy) * m + EMAy

            VALUE: new value being added.
            EMAy: Exponential MA of yesterday
            m: multiplier = smoothing / (period + 1)

        This implementation starts from the first data point.
    '''
    def __init__(self, period, smoothing=2.0):
        '''
            period = number of days to track the moving average.
            smoothing = smoothing factor used in the multiplier calculation. default is 2.0
        '''
        if not isinstance(period, int) or period < 1:
            raise ValueError("period must be an integer and greater than 0")
        if not isinstance(smoothing, (int, float)) or smoothing < 1.0:
            raise ValueError("smoothing must be a rational number and >= 1.0")

        self._average = None
        self._period = period
        self._smoothing = smoothing
        self._multiplier = smoothing / (period + 1)

    def update(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("value is non-numeric or complex.")

        if self._average is None:
            self._average = value

        self.average = (value - self._average) * self._multiplier + self._average

    @property
    def average(self):
        return self._average if self._average is not None else 0.0
