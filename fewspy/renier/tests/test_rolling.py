import pandas as pd


def test_rolling():
    """
    pandas.DataFrame.rolling(center=.., closed=..)

    closed (str, default='right')
      'right' = the first point in the window is excluded from calculations.
      'left' = the last point in the window is excluded from calculations.
      'both' = no points in the window are excluded from calculations.
      'neither' = the first and last points in the window are excluded from calculations.

    center (bool, default=False)
      False = set the window labels as the right edge of the window index.
      True = set the window labels as the center of the window index.

    min_periods (int, default=see text below)
    Minimum number of observations in window required to have a value; otherwise, result is np.nan.
    For a window that is specified by an offset, min_periods will default to 1.
    For a window that is specified by an integer, min_periods will default to the size of the window.
    """
    df = pd.DataFrame({"data": [0, 1, 2, 3, 4]})
    df.index = [
        pd.Timestamp("20130101 09:00:00"),
        pd.Timestamp("20130101 09:00:01"),
        pd.Timestamp("20130101 09:00:03"),
        pd.Timestamp("20130101 09:00:04"),
        pd.Timestamp("20130101 09:00:06"),
    ]

    df["sum_1sec_right"] = df["data"].rolling(window="1s", closed="right", min_periods=2).sum()
    df["sum_2sec_right"] = df["data"].rolling(window="2s", closed="right", min_periods=2).sum()
    df["sum_1sec_both"] = df["data"].rolling(window="1s", closed="both", min_periods=2).sum()
    df["sum_2sec_both"] = df["data"].rolling(window="2s", closed="both", min_periods=2).sum()

    # index             data    sum_1sec_right  sum_2sec_right  sum_1sec_both   sum_2sec_both
    # 20130101 09:00:00 0       nan             nan             nan             nan   <-- nans due to min_periods=2
    # 20130101 09:00:01 1       nan             1               1               1
    # 20130101 09:00:03 2       nan             nan             nan             3
    # 20130101 09:00:04 3       nan             5               5               5
    # 20130101 09:00:06 4       nan             nan             nan             7
