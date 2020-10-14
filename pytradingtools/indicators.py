from enum import Enum

#==============================================#
    # In this file (in-order as they appear):
    #       EnvelopeState(Enum)
    #       Envelope
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

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
