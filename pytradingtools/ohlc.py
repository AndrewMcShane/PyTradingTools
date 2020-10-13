from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import datetime
#==============================================#
    # In this file (in-order as they appear):
    #       OhlcData(dataclass)
    #       OhlcService(ABCMeta)
#==============================================#


#==============================================#
# START CLASSES
#==============================================#

@dataclass
class OhlcData:
    '''
    Contains information about the open, high, low, close, and volume on a specified `date`.
    '''
    date: datetime.date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float

    def __init__(self, date, open_price, high, low, close, volume = 0):
        '''
            date: `datetime.date`
                the date of the data. Can be `None`.

            open_price: `float`
                the price at market open.

            high: `float`
                the highest price during the trading period.

            low `float`
                the lowest price during the trading period.

            close `float`
                the price at the end of the  trading day.

            volume: `float`
                the amount of asset that has been traded.
        '''
        self.date = date
        self.open_price = open_price
        self.high_price = high
        self.low_price = low
        self.close_price = close
        self.volume = volume

class OhlcService(metaclass=ABCMeta):
    '''
    Abstract Base Class for an OHLC Service.

    Abstract Methods
    ----------------

    getData:
        return a list of OhlcData objects
    '''
    @abstractmethod
    def getData(self):
        '''
        returns a list of OhlcData objects.
        '''
