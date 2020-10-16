import unittest
# pylint: disable=line-too-long
from pytradingtools.indicators import Envelope, EnvelopeState, TradeSignal

class TestEnvelope(unittest.TestCase):
    '''Test cases for the Envelope utility'''
    def test_initialization(self):
        '''Test the initialization of the Envelope'''
        self.assertRaises(ValueError, Envelope, (1.0, 1.0, 1.0))
        self.assertRaises(ValueError, Envelope, 5j)
        self.assertRaises(ValueError, Envelope, "hello world")

        envelope = Envelope()
        self.assertEqual(envelope.state, EnvelopeState.between)

    def test_update(self):
        '''Test the update method with various deltas'''
        delta = 0.1
        deltaTuple = (0.1, 0.05)

        envelope = Envelope(delta)

        envelope.update(100, 120)
        self.assertAlmostEqual(envelope.aboveBound, 110)
        self.assertAlmostEqual(envelope.belowBound, 90)
        self.assertEqual(envelope.state, EnvelopeState.above)

        self.assertEqual(envelope.stateAsSignal(), TradeSignal.buy)
        self.assertEqual(envelope.stateAsSignal(invert=True), TradeSignal.sell)

        envelope.update(100, 101)
        self.assertAlmostEqual(envelope.state, EnvelopeState.between)

        envelope = Envelope(deltaTuple)
        envelope.update(100, 90)
        self.assertAlmostEqual(envelope.aboveBound, 110)
        self.assertAlmostEqual(envelope.belowBound, 95)
        self.assertEqual(envelope.state, EnvelopeState.below)

        self.assertEqual(envelope.stateAsSignal(), TradeSignal.sell)
        self.assertEqual(envelope.stateAsSignal(invert=True), TradeSignal.buy)
