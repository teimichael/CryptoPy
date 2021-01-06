import numpy as np
import talib as ta


# Indicators
class Indicator:
    def __init__(self, records, length_limit):
        # Ignore current time point record (only consider complete k-lines)
        records = records[:-1]

        # Open Price List
        self.open = np.asarray([r[1] for r in records])

        # High Price List
        self.high = np.asarray([r[2] for r in records])

        # Low Price List
        self.low = np.asarray([r[3] for r in records])

        # Close Price List
        self.close = np.asarray([r[4] for r in records])

        # Bollinger Bands (Close)
        bb = ta.BBANDS(self.close, timeperiod=60, nbdevup=2, nbdevdn=2)
        self.bbUpper = fill_none(bb[0][-length_limit:])
        self.bbLower = fill_none(bb[2][-length_limit:])

        self.open = self.open[-length_limit:]
        self.high = self.high[-length_limit:]
        self.low = self.low[-length_limit:]
        self.close = self.close[-length_limit:]


def fill_none(series, value=0) -> np.ndarray:
    return np.asarray([value if v is None else v for v in series])
