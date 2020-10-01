'''
Moving Average module for the trading tools.
'''

#==============================================#
'''
    In this file (in-order as they appear):
        MovingAverage(ABCMeta)
        SimpleMovingAverage(MovingAverage)
'''
#==============================================#

### IMPORTS ###
from abc import ABCMeta
from pytradingtools.utilities import RollingQueue

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
    def update(self, value) : pass

    @property
    @abstractmethod
    def average(self) : pass

class SimpleMovingAverage(MovingAverage):
    '''
        Averages the values of the given period.
    '''
    def __init__(self, period):
        '''
        period: 
            the amount of data to use for the moving average value.    
        '''
        self._recip_capacity = 1.0 / period
        self._average = 0.0
        self._queue = RollingQueue(period)
        
    def update(self, value):
        '''
        Update the moving average with the value given.

        Raises ValueError if value is non-numeric, or complex.
        '''
        if type(value) not in [int, float]:
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
        return self._average
    
    @property
    def period(self):
        return self._queue.capacity