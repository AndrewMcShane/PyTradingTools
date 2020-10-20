from enum import Enum
from pytradingtools.movingaverage import SmoothedMovingAverage, SimpleMovingAverage, ExponentialMovingAverage
from pytradingtools.utilities import RollingQueue
#==============================================#
    # In this file (in-order as they appear):
    #       OscillatorSignal(Enum)
    #       RelativeStrengthIndex
    #       CutlerRSI
    #       MACD
    #       WilliamsPercentRange
    #       OnBalanceVolume
    #       ADLine
    #       StochasticOscillator
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
    def __init__(self, period=14, oversold=30, overbought=30):
        '''
        period : `int` the number of days to use as lookback.

        oversold: `int, float` range 0-100, RSI index where the asset is oversold. Default 30.

        overbought `int, float` range 0-100, RSI index where the asset is overbought. Default 70.
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

        self._oversold = oversold
        self._overbought = overbought

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

        # Avoid 0-division
        if self._down.average > 0.0:
            self._rs = self._up.average / self._down.average
            self._rsi = 100 - (100 / (1 + self._rs))
        else:
            # if there have been 0 down days, then we have a special-case 100 RSI.
            self._rsi = 100

        self._lastPrice = value

    @property
    def rsi(self):
        '''
        Get the Relative Strength Index (RSI).

        Ranges between 0-100
        '''
        return self._rsi

    @property
    def rs(self):
        '''Get the Relative Strength without indexing.'''
        return self._rs

    @property
    def state(self):
        '''Returns the `OscillatorSignal` of the most recent RSI value.'''
        if self._rsi >= self._overbought:
            return OscillatorSignal.overbought
        elif self._rsi <= self._oversold:
            return OscillatorSignal.oversold
        else:
            return OscillatorSignal.nothing

class CutlerRSI(RelativeStrengthIndex):
    '''
    Relative Strength Index calculated using Cutler's method which employs an SMA instead of EMA.

    Cutler's RSI evades the data-length issue of 50 days worth of RSI being different than 500
    due to the nature of EMA having "residual" data carryover from beyond a smoothing period.
    '''
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__(period, oversold, overbought)

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

        self._up.update(up)
        self._down.update(down)

        # Avoid 0-division
        if self._down.average > 0.0:
            self._rs = self._up.average / self._down.average
            self._rsi = 100 - (100 / (1 + self._rs))
        else:
            # if there have been 0 down days, then we have a special-case 100 RSI.
            self._rsi = 100

        self._lastPrice = value


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

class OnBalanceVolume:
    '''
    Provides a running total of volume,
    shows whether money is moving in or out of an asset.

    OBV = OBVprev +

        {
            volume  if CLOSE > CLOSEprev,
            0       if CLOSE = CLOSEprev,
            -volume if CLOSE < CLOSEprev
        }
    '''
    def __init__(self):
        self._obv = 0.0
        self._lastPrice = 0.0

    def update(self, volume, close):
        '''
        Update the OBV:

        volume: `int` shares of a holding exchanged on a given day.

        close: `float` the closing price of the market.
        '''
        if close > self._lastPrice:
            self._obv += volume
        elif close < self._lastPrice:
            self._obv -= volume

        self._lastPrice = close

    @property
    def value(self):
        '''Return the value of the OBV'''
        return self._obv

class ADLine:
    '''
    Accumulation / Distribution Line.

    Hints supply and demand, looking at where the price closed compared to the price action.

    A Rising A/D can confirm an uptrend.
    A falling A/D can confirm a downtrend.

    If a price is rising but A/D falls, it signals a decline.
    If a price is falling but A/D rises, it signals underlying strength.
    '''
    def __init__(self):
        self._ad = 0.0

    def update(self, close, high, low, volume):
        '''
        close: the closing price of the last market day.

        high: the highest price in the last market day.

        low: the lowest price in the last market day.

        volume: the volume for the last market day.
        '''
        self._ad += (((close - low) - (high - close)) / (high - low)) * volume

    @property
    def value(self):
        '''returns the A/D value.'''
        return self._ad

class StochasticOscillator:
    '''
    Compares closing price to price action over a given period.

    attempts to catch new highes and lows in a market period.

        %K = (Close - LowN) / (HighN - LowN)

    Close: most recent close price

    LowN: the lowest price traded over N days

    HighN: the highest price traded over N days

    N typically = 14

    %K 0-100 range

    Prefer RSI in trending markets, but stochastics in choppy markets.

    Visual Aids tend to use a 3-day SMA in conjunction to get a better idea of momentum.
    '''
    def __init__(self, period=14, oversold=20, overbought=80):
        '''
        period: `int` the number of days to look back at prices

        oversold: `int` %K value to signal oversold when %K <= oversold

        overbought: `int` %K value to signal overbought when %K >= overbought
        '''
        self._lows = RollingQueue(period)
        self._highs = RollingQueue(period)
        self._k = 0

        self._oversold = oversold
        self._overbought = overbought

    def update(self, close, high, low):
        '''
        close: `float` the last closing price.

        high: `float` the highest price traded on a day.

        low: `float` the lowest price traded on a day.
        '''
        self._lows.enqueue(low)
        self._highs.enqueue(high)

        l = min(self._lows)
        h = max(self._highs)
        self._k = ((close - l) / (h - l)) * 100

    @property
    def percentk(self):
        '''returns the %K value'''
        return self._k

    @property
    def state(self):
        '''Returns the `OscillatorSignal` of the %K value'''
        if self._k >= self._overbought:
            return OscillatorSignal.overbought
        if self._k <= self._oversold:
            return OscillatorSignal.oversold

        return OscillatorSignal.nothing
