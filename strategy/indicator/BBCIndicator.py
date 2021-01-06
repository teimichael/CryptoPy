import numpy as np
import talib as ta

# Indicators for Bollinger Bands Compound Strategy
from talib._ta_lib import MA_Type


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

        # MA
        self.fastMA = remove_none(ta.EMA(self.close, 3)[-length_limit:])
        self.bbBasis = remove_none(ta.SMA(self.close, 20)[-length_limit:])

        # Bollinger Bands (Close)
        bb = ta.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=MA_Type.SMA)
        self.bbUpper = remove_none(bb[0])[-length_limit:]
        self.bbLower = remove_none(bb[2])[-length_limit:]

        # BB spread and average spread
        spread = self.bbUpper - self.bbLower
        # Squeeze indication
        sqz_length = 100
        sqz_threshold = 50
        avg_spread = ta.SMA(spread, sqz_length)
        # BB relative %width for Squeeze indication
        self.bbSqueeze = spread / avg_spread * 100

        # Calculate Upper and Lower band painting offsets based on 50% of atr.
        bb_offset = ta.ATR(self.high, self.low, self.close, timeperiod=14) * 0.5
        bb_offset = bb_offset[-length_limit:]
        self.bbSqzUpper = self.bbUpper + bb_offset
        self.bbSqzLower = self.bbLower - bb_offset

        # (High + Low) / 2
        hl2 = (self.high + self.low) / 2

        # Oscillator
        sma_fast_hl2 = fill_none(ta.SMA(hl2, 5)[-length_limit:])
        sma_slow_hl2 = fill_none(ta.SMA(hl2, 34)[-length_limit:])
        sma_diff = sma_fast_hl2 - sma_slow_hl2

        # Oscillator Direction
        if sma_diff[-1] >= 0:
            if sma_diff[-1] > sma_diff[-2]:
                osc = 1
            else:
                osc = 2
        else:
            if sma_diff[-1] > sma_diff[-2]:
                osc = -1
            else:
                osc = -2
        self.osc = osc

        self.open = self.open[-length_limit:]
        self.high = self.high[-length_limit:]
        self.low = self.low[-length_limit:]
        self.close = self.close[-length_limit:]


def remove_none(series) -> np.ndarray:
    arr = np.asarray(series)
    return arr[~np.isnan(arr)]


def fill_none(series, value=0) -> np.ndarray:
    return np.asarray([value if v is None else v for v in series])
