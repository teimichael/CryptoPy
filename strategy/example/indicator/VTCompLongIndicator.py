import numpy as np
import talib as ta

from talib._ta_lib import MA_Type


# Indicators for Vegas Tunnel Compound Strategy (long)
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

        # MACD DIF (Close)
        self.macd_dif = fill_none(ta.MACD(self.close, 48, 56)[0][-length_limit:])[-1]

        # EMA (Close)
        self.ema36 = fill_none(ta.EMA(self.close, 36)[-length_limit:])
        self.ema144 = fill_none(ta.EMA(self.close, 144)[-length_limit:])
        self.ema169 = fill_none(ta.EMA(self.close, 169)[-length_limit:])
        self.ema576 = fill_none(ta.EMA(self.close, 576)[-length_limit:])
        self.ema676 = fill_none(ta.EMA(self.close, 676)[-length_limit:])

        # Bollinger Bands (Close)
        bb = ta.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=MA_Type.SMA)
        self.bbUpper = fill_none(bb[0][-length_limit:])
        self.bbLower = fill_none(bb[2][-length_limit:])

        self.open = self.open[-length_limit:]
        self.high = self.high[-length_limit:]
        self.low = self.low[-length_limit:]
        self.close = self.close[-length_limit:]


# Indicator for check
class IndicatorCheck:
    def __init__(self, records, length_limit):
        last = records[-1]

        # Close Price List
        # Ignore current time point record for calculating indicators(only consider complete k-lines)
        self.close = np.asarray([r[4] for r in records[:-1]])

        self.ema144 = fill_none(ta.EMA(self.close, 144)[-length_limit:])
        self.ema576 = fill_none(ta.EMA(self.close, 576)[-length_limit:])

        # Bollinger Bands (Close)
        bb = ta.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.bbUpper = fill_none(bb[0][-length_limit:])
        self.bbLower = fill_none(bb[2][-length_limit:])

        # Append the latest record
        self.close = np.append(self.close, last[4])

        self.close = self.close[-length_limit:]


def fill_none(series, value=0) -> np.ndarray:
    return np.asarray([value if v is None else v for v in series])
