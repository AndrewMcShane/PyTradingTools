from pytradingtools.movingaverage import SmoothedMovingAverage, SimpleMovingAverage

#==============================================#
    # In this file (in-order as they appear):
    #       RelativeStrengthIndex
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class RelativeStrengthIndex:
    '''
    Calculates RSI.
    While there are less values entered than the period, uses SMA,
    but switches to SMMA henceforth.

    RSI = 100 - 100 / (1 + RS)

    RS = SMMA(up, n) / SMMA(down,n)

    n = period
    '''
    def __init__(self, period=14):
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
