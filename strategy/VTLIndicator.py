import numpy as np
import talib as ta


# Indicators
class Indicator:
    def __init__(self, records, length_limit):
        self.__length_limit = length_limit

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
        self.macd_dif = self.__fill_none(ta.MACD(self.close, 48, 56)[0][-self.__length_limit:])[-1]

        # EMA (Close)
        self.ema36 = self.__fill_none(ta.EMA(self.close, 36)[-self.__length_limit:])
        self.ema144 = self.__fill_none(ta.EMA(self.close, 144)[-self.__length_limit:])
        self.ema169 = self.__fill_none(ta.EMA(self.close, 169)[-self.__length_limit:])
        self.ema576 = self.__fill_none(ta.EMA(self.close, 576)[-self.__length_limit:])
        self.ema676 = self.__fill_none(ta.EMA(self.close, 676)[-self.__length_limit:])

        # Bollinger Bands (Close)
        bb = ta.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.bbUpper = self.__fill_none(bb[0][-self.__length_limit:])
        self.bbLower = self.__fill_none(bb[2][-self.__length_limit:])

        self.open = self.open[-self.__length_limit:]
        self.high = self.high[-self.__length_limit:]
        self.low = self.low[-self.__length_limit:]
        self.close = self.close[-self.__length_limit:]

    @staticmethod
    def __fill_none(series, value=0) -> np.ndarray:
        return np.asarray([value if v is None else v for v in series])
