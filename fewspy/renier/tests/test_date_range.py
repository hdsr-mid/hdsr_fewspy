from gapfinder.manager import Manager

import pandas as pd


def test_date_range():
    startdate_obj = pd.Timestamp("2010-04-27 00:00:00")
    enddate_obj = pd.Timestamp("2010-04-27 05:00:00")
    frequency = pd.Timedelta(hours=1, seconds=10, milliseconds=100)
    ranges, frequency_used = Manager._create_date_ranges(
        startdate_obj=startdate_obj, enddate_obj=enddate_obj, frequency=frequency
    )
    assert frequency_used == pd.Timedelta("0 days 01:00:10")  # note that no milliseconds exist
    assert ranges == [
        (pd.Timestamp("2010-04-27 00:00:00"), pd.Timestamp("2010-04-27 01:00:10")),
        (pd.Timestamp("2010-04-27 01:00:10"), pd.Timestamp("2010-04-27 02:00:20")),
        (pd.Timestamp("2010-04-27 02:00:20"), pd.Timestamp("2010-04-27 03:00:30")),
        (pd.Timestamp("2010-04-27 03:00:30"), pd.Timestamp("2010-04-27 04:00:40")),
        (pd.Timestamp("2010-04-27 04:00:40"), pd.Timestamp("2010-04-27 05:00:00")),
    ]

    for index, _range in enumerate(ranges):
        range_start = _range[0]
        range_end = _range[1]
        _is_last_range = index == len(ranges) - 1
        if not _is_last_range:
            assert range_end - range_start == frequency_used
        else:
            assert range_end - range_start <= frequency_used
