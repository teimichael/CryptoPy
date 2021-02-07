import numpy as np
import talib as ta


# Indicators for Vegas Tunnel Classic Strategy
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

        # EMA (Close)
        self.ema21 = fill_none(ta.EMA(self.close, 21)[-length_limit:])
        self.ema34 = fill_none(ta.EMA(self.close, 34)[-length_limit:])
        self.ema144 = fill_none(ta.EMA(self.close, 144)[-length_limit:])
        self.ema169 = fill_none(ta.EMA(self.close, 169)[-length_limit:])

        self.open = self.open[-length_limit:]
        self.high = self.high[-length_limit:]
        self.low = self.low[-length_limit:]
        self.close = self.close[-length_limit:]


def fill_none(series, value=0) -> np.ndarray:
    return np.asarray([value if v is None else v for v in series])
