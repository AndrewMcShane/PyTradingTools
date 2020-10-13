from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from collections import deque
import datetime
#==============================================#
    # In this file (in-order as they appear):
    #       OhlcData(dataclass)
    #       OhlcService(ABCMeta)
    #       OhlcFileReader(OhlcService)
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

class OhlcFileReader(OhlcService):
    '''
    Reads OHLC data from a file source, transforming it into a list of OhlcData.
    '''
    def __init__(self, file, ignoreLines=0, delimiter=None, dateForm='%Y-%m-%d', hasVolume=True, ascending=True):
        '''
        Assumes file input to follow this order (line-by-line):

            DateTime, Open, High, Low, Close, Volume

        raises ValueError if format is incorrect.

        Params
        ------

        `file`: `str`
            Path to the source file. Raises OSError if there is a problem opening the file.

        `ignoreLines`: `int`
            how many lines of the file should be skipped when starting to read.
            default=0. If the first line of the file you're reading in is column labels,
            you will want ignoreLines = 1. Raises ValueError if EOF is hit.

        `delimiter`: `str`
            separator between data on the same line. Default is any whitespace.

        `dateForm`: `str`
            Default `%Y-%m-%d`. The format `datetime.strptime` should use when parsing the date.

        `hasVolume`: `bool`
            Default True. If false, will specify that the input file has no volume column.

        `ascending`: `bool`
            Default True. Is the data in the file in ascending (oldest first) or descending order?
            In either case, the resulting data will be in ascending (oldest first) order.
        '''

        self.data = []
        # deque has o(1) insert left, compared to o(n) insert(0) of list.
        dataDeq = deque()
        # The expected number of elements in each line
        expectedLen = 6
        if not hasVolume:
            expectedLen -= 1

        # Try and open the file
        with open(file) as f:
            # Skip the lines to ignore:
            for _ in range(ignoreLines):
                next(f)
            # Parse out every line after:
            for line in f:
                # split delimit
                cols = line.split(delimiter)

                if not len(cols) == expectedLen:
                    raise ValueError("Line {} contains {} elements but {} were expected.".format(line, len(cols), expectedLen))

                # Go through the columns:
                _date = datetime.datetime.strptime(cols[0], dateForm)
                _open = float(cols[1])
                _high = float(cols[2])
                _low = float(cols[3])
                _close = float(cols[4])
                _volume = 0
                if hasVolume:
                    _volume = float(cols[5])

                # Create the ohlc object:
                ohlc = OhlcData(_date, _open, _high, _low, _close, _volume)
                # Add to the list:
                if ascending:
                    dataDeq.append(ohlc)
                else:
                    dataDeq.appendleft(ohlc)

        # With the file read, convert the deque into the list:
        self.data = list(dataDeq)


    def getData(self):
        return self.data
   