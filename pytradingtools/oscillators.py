from enum import Enum
from pytradingtools.movingaverage import SmoothedMovingAverage, SimpleMovingAverage, ExponentialMovingAverage
from pytradingtools.utilities import RollingQueue
#==============================================#
    # In this file (in-order as they appear):
    #       OscillatorSignal(Enum)
    #       RelativeStrengthIndex
    #       MACD
    #       WilliamsPercentRange
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class OscillatorSignal(Enum):
    '''
    Used with oscillators to derive a signal of an index's overbought/oversold status.
    '''
    overbought = 0
    oversold = 1
    nothing = 2

class RelativeStrengthIndex:
    '''
    Calculates RSI.
    While there are less values entered than the period, uses SMA,
    but switches to SMMA henceforth.

    RSI = 100 - 100 / (1 + RS)

    RS = SMMA(up, n) / SMMA(down,n)

    n = period
    '''
    def __init__(self, period=14, oversold=0.3, overbought=0.7):
        '''
        period : `int` the number of days to use as lookback.

        oversold: `float` range 0-1, RSI index where the asset is oversold. Default 0.3.

        overbought `float` range 0-1, RSI index where the asset is overbought. Default 0.7.
        '''
        self._period = period
        # Cache for speed
        self._recip_period = 1 / self._period

        self._lastPrice = None
        # When starting out, use SMA until accurate enough to use SMMA.
        self._up = SimpleMovingAverage(self._period)
        self._down = SimpleMovingAverage(self._period)

        self._rs = 0.0
        self._rsi = 0.0
        self._isaccurate = False

        # TODO: Add overbought/sold and state getter.

    def update(self, value):
        '''
        Update the RSI

        Note:
            Will not be accurate until the period window is met.
        '''
        if self._lastPrice is None:
            self._lastPrice = value

        # Update the up and down
        up = 0.0
        down = 0.0
        if value > self._lastPrice:
            up = value - self._lastPrice
        elif value < self._lastPrice:
            # When down, reverse the subtraction:
            down = self._lastPrice - value

        if not self._isaccurate and self._up.isaccurate:
            # Switch over to using SMMA instead of SMA
            old_up = self._up.average
            old_down = self._down.average
            self._up = SmoothedMovingAverage(self._period)
            self._down = SmoothedMovingAverage(self._period)
            self._up.update(old_up)
            self._down.update(old_down)

            self._isaccurate = True

        self._up.update(up)
        self._down.update(down)

        rs = 0
        # Avoid 0-division
        if self._down.average > 0.0:
            rs = self._up.average / self._down.average
        self._rs = rs
        self._rsi = 100 - (100 / (1 + self._rs))

    @property
    def rsi(self):
        '''
        Get the Relative Strength Index (RSI).

        Ranges between 0-1
        '''
        return self._rsi

    @property
    def rs(self):
        '''
        Get the Relative Strength without indexing.
        '''
        return self._rs

class MACD:
    '''
    Moving Average Convergence Divergence Oscillator.

    Oscillator that displays the difference between 2 Moving Averages,
    typically between a 12-day and 26-day EMA.
    '''
    def __init__(self, short=12, long=26):
        '''
        short: `int, MovingAverage` the period or moving average itself to be used
        as the shorter of the two moving averages. If an `int` is given, this will use an EMA internally.

        long: `int, MovingAverage` the period of moving average itself to be used
        as the longer of the two moving averages. If an `int` is given, this will use an EMA internally.

        Examples:

            MACD(ExponentialMovingAverage(12), 26)
            MACD()
            MACD(SimpleMovingAverage(12), SimpleMovingAverage(26))
        '''
        if isinstance(short, int):
            self.short = ExponentialMovingAverage(short)
        else:
            self.short = short

        if isinstance(long, int):
            self.long = ExponentialMovingAverage(long)
        else:
            self.long = long

        self._macd = 0.0

    def update(self, value):
        '''
        value : `float` the market price for the MACD to use to calculate the index.
        '''
        self.short.update(value)
        self.long.update(value)

        self._macd = self.short.average - self.long.average

    @property
    def macd(self):
        '''
        Returns the most recent calculated output index of the `MACD.update()` method.
        '''
        return self._macd

class WilliamsPercentRange:
    '''
    Williams %R formula:

        Highest - Close / Highest - Lowest

    Highest = Highest price over the period

    Close = Closing price for the most recent trading day

    Lowest = Lowest price over the period

    Typical Period = 14 days
    '''
    def __init__(self, period=14, overbought=-20, oversold=-80):
        '''
        period : `int` The number of days to lookback when calculating %R

        overbought : `int,float` The %R value that specifies if the asset is overbought when %R is greater.

        oversold : `int,float` The %R value that specifies if the asset is oversold when the %R is lesser.
        '''
        self._lookback = RollingQueue(period)
        self._period = period
        self._percentRange = 0.0

        self._overbought = overbought
        self._oversold = oversold

    def update(self, value):
        '''
        value: `float` the latest market close price.
        '''
        highest = max(self._lookback)
        lowest = min(self._lookback)
        self._percentRange = (highest - value) / (highest - lowest)

    @property
    def range(self):
        '''
        Returns the most recently calculated %R value.

        %R moves between 0 and -100

        0 > %R > -20 typically means overbought

        -80 > %R > -100 typically means oversold
        '''
        return self._percentRange

    @property
    def state(self):
        '''
        Returns the `OscillatorSignal` of the %R value.
        '''
        if self._percentRange >= self._overbought:
            return OscillatorSignal.overbought
        elif self._percentRange <= self._oversold:
            return OscillatorSignal.oversold
        else:
            return OscillatorSignal.nothing
