from enum import Enum

from pytradingtools.movingaverage import MovingAverage, SimpleMovingAverage
from pytradingtools.utilities import RollingStats, RunningStats

#==============================================#
    # In this file (in-order as they appear):
    #       TradeSignal(Enum)
    #       EnvelopeState(Enum)
    #       Envelope
    #       MovingAverageCrossover
    #       BollingerBands
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class TradeSignal(Enum):
    '''
    `Enum` The current state of an indicator.

    Values
    ------

    `buy`: `0`

    `sell`: `1`

    `hold`: `2`
    '''
    buy = 0
    sell = 1
    hold = 2

class EnvelopeState(Enum):
    '''
    Defines the current state of an envelope utility.

    Values
    ------
    above: the input value is above the envelope

    below: the input value is below the envelope

    between: the input is inside the envelope
    '''
    above = 0
    below = 1
    between = 2

class Envelope:
    '''
    An envelope plots trend lines above and below a source by a fixed percent.

    This envelope implementation allows for uniform and independent percents (as tuple)
    '''
    def __init__(self, delta = 0.05):
        '''
        delta: percentage to vary the trend by.

        examples:

            # Place the envelope above and below by 5%:
            Envelope(0.05)
            # Place the envelope above by 5%, below by 10%:
            Envelope((0.05, 0.10))
        '''
        self._abovePercent = 0.0
        self._belowPercent = 0.0
        self._state = EnvelopeState.between
        self._aboveBound = 0.0
        self._belowBound = 0.0

        if isinstance(delta, tuple):
            if len(delta) != 2:
                raise ValueError("Tuple must contain 2 values (above%, below%)")
            self._abovePercent = delta[0]
            self._belowPercent = delta[1]
        elif isinstance(delta, (int, float)):
            self._abovePercent = delta
            self._belowPercent = delta
        else:
            raise ValueError("delta must be a non-complex number or tuple")

    def update(self, average, value):
        '''
        update the envelope with the trend average, and the value (price).

        average: `float`
            The Moving-Average's value

        value: `float`
            The value to check against the envelope. (Usually the market price)
        '''
        self._aboveBound = average + (average * self._abovePercent)
        self._belowBound = average - (average * self._belowPercent)

        if value >= self._aboveBound:
            self._state = EnvelopeState.above
        elif value <= self._belowBound:
            self._state = EnvelopeState.below
        else:
            self._state = EnvelopeState.between

    @property
    def state(self):
        '''
        get the current state of the envelope
        '''
        return self._state

    def stateAsSignal(self, invert=False):
        '''
        Get the state of the envelope as a `TradeSignal`

        `invert`:  `bool`
            Default False. If true, a 'normal' buy signal will return sell, and vice versa. hold will remain the same.
        '''
        # Trade signal and enum state share values (purposefully)
        # this allows moving between one and the other.
        signal = TradeSignal(self._state.value)
        if invert:
            if signal == TradeSignal.buy:
                signal = TradeSignal.sell
            elif signal == TradeSignal.sell:
                signal = TradeSignal.buy
        return signal

    @property
    def aboveBound(self):
        '''
        get the value of the top boundary
        '''
        return self._aboveBound

    @property
    def belowBound(self):
        '''
        get the value of the bottom boundary
        '''
        return self._belowBound

class MovingAverageCrossover:
    '''
    A simple moving average crossover indicator.

    Uses two moving averages - 'short' and 'long'.
    If the value of the short crosses under the long, that signals a sell opporunity.
    If the value of the short crosses over the long, that signals a buy opporunity.

    '''
    def __init__(self, short, long, invertSignal=False):
        '''
        short: `int`, `MovingAverage`
            The Moving Average with the shorter of the two periods.

        long: `int`, `MovingAverage`
            The Moving Average with the longer of the two periods.

        invertSignal: `bool`
            Default False. If true, will invert the `TradeSignal`

        Raises a value error if short, long <= 0

        If an integer is supplied in either case, a `SimpleMovingAverage` of that length will be created.
        '''
        if isinstance(short, MovingAverage):
            self.short = short
        elif isinstance(short, int):
            self.short = SimpleMovingAverage(short)
        else:
            raise ValueError("short must be of type int or MovingAverage")

        if isinstance(long, MovingAverage):
            self.long = long
        elif isinstance(long, int):
            self.long = SimpleMovingAverage(long)
        else:
            raise ValueError("long must be of type int or MovingAverage")

        self._signal = TradeSignal.hold
        # If the signal changes in the most recent update, then this is 'fresh'
        self._freshSignal = False
        self.invertedSignal = invertSignal

    def update(self, value):
        '''
        Update the indicator with a value (usually market price).
        Handles updating of the short and long MovingAverages

        `returns` the most recent signal, same result as calling `signal`
        '''
        self.short.update(value)
        self.long.update(value)
        # Default that the signal is stale until proven fresh.
        self._freshSignal = False

        signal = TradeSignal.hold

        if self.short.average < self.long.average:
            signal = TradeSignal.sell
            if self.invertedSignal:
                signal = TradeSignal.buy
        else:
            signal = TradeSignal.buy
            if self.invertedSignal:
                signal = TradeSignal.sell

        if self._signal != signal:
            self._freshSignal = True

        self._signal = signal
        return self._signal

    def setInverted(self, invertSignal):
        '''Sets whether the signal should be inverted or not.'''
        self.invertedSignal  = invertSignal

    @property
    def signal(self):
        '''
        returns the most recent trade signal.
        To only get a buy/sell signal on the frame that it happens, use `strictSignal`
        '''
        return self._signal

    @property
    def strictSignal(self):
        '''
        Get the signal only if it has changed in the most recent `update`.
        This allows it to act as a trigger instead of a constant signal.
        Logic:

            if signal(n-1) != signal(n): return signal
            else return TradeSignal.hold
        '''
        if self._freshSignal:
            return self._signal
        return TradeSignal.hold

class BollingerBands:
    '''
    TODO
    '''
    