import numpy as np
import pandas as pd


def crossed(series1, series2, direction):
    if not (direction in ['above', 'below']):
        raise Exception("Must identify direction (above or below).")

    if isinstance(series1, np.ndarray):
        series1 = pd.Series(series1)

    if isinstance(series2, (float, int, np.ndarray, np.integer, np.floating)):
        series2 = pd.Series(index=series1.index, data=series2)

    s = None
    if direction == "above":
        s = pd.Series((series1 > series2) & (
                series1.shift(1) <= series2.shift(1)))

    elif direction == "below":
        s = pd.Series((series1 < series2) & (
                series1.shift(1) >= series2.shift(1)))

    return s


# series 1 crossed above series 2
def crossed_above(series1, series2):
    return crossed(series1, series2, "above")


# series1 crossed below series 2
def crossed_below(series1, series2):
    return crossed(series1, series2, "below")
