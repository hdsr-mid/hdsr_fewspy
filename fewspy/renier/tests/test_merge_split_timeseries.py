from gapfinder import exceptions
from gapfinder.analysers.classify_timeseries import QualifyTimeseries

import pandas as pd
import pytest


def test_merge_split_case1():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                1: pd.Timestamp("2014-06-30 00:00:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2014-06-30 10:57:54+0000", tz="Etc/GMT-0"),
            },
            "end": {
                1: pd.Timestamp("2014-06-30 00:03:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2014-06-30 18:00:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {1: pd.Timedelta("0 days 02:55:21"), 2: pd.Timedelta("0 days 07:02:06")},
        }
    )

    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                1: pd.Timestamp("2014-06-30 07:45:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2014-06-30 10:45:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2014-06-30 18:15:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2014-06-30 18:45:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                1: pd.Timestamp("2014-06-30 10:45:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2014-06-30 18:00:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2014-06-30 18:45:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2014-06-30 20:30:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                1: pd.Timedelta("0 days 03:00:00"),
                2: pd.Timedelta("0 days 07:15:00"),
                3: pd.Timedelta("0 days 00:30:00"),
                4: pd.Timedelta("0 days 01:45:00"),
            },
        }
    )
    wis_periods = [
        (
            pd.Timestamp("2014-06-28 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2014-06-30 21:00:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test1",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )


def test_merge_split_case2():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                0: pd.Timestamp("2017-05-17 07:21:00+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2017-05-17 13:01:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2017-05-18 01:31:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                0: pd.Timestamp("2017-05-17 12:01:00+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2017-05-18 00:31:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2017-05-18 12:01:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                0: pd.Timedelta("0 days 04:39:51"),
                1: pd.Timedelta("0 days 11:30:00"),
                2: pd.Timedelta("0 days 10:29:59"),
            },
        }
    )
    # period 1 overlaps with period 2 which will result in GapError:
    #   int_loc_par=test2, error=quarter_gaps: found 1 rows where not (start>=end_previous_row)
    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                1: pd.Timestamp("2017-05-17 15:45:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2017-05-17 13:15:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                1: pd.Timestamp("2017-05-17 16:15:00+0000", tz="Etc/GMT-0"),  # note error: end
                2: pd.Timestamp("2017-05-19 13:15:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                1: pd.Timedelta("0 days 00:30:00"),
                2: pd.Timedelta("2 days 00:00:00"),
            },
        }
    )
    wis_periods = [
        (
            pd.Timestamp("2015-05-17 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2018-05-20 00:00:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    with pytest.raises(exceptions.TsManagerGapError):
        QualifyTimeseries.classify_subsequent_periods(
            int_loc_par="test2",
            wis_periods=wis_periods,
            dfs_normal_gaps=[df_normal_gaps],
            dfs_quarter_gaps=[df_quarter_gaps],
        )


def test_merge_split_case3():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                1794: pd.Timestamp("2018-03-25 13:00:21+0000", tz="Etc/GMT-0"),
                1795: pd.Timestamp("2018-03-26 01:30:21+0000", tz="Etc/GMT-0"),
                1796: pd.Timestamp("2018-03-26 13:00:22+0000", tz="Etc/GMT-0"),
                1797: pd.Timestamp("2018-03-27 01:30:23+0000", tz="Etc/GMT-0"),
                1798: pd.Timestamp("2018-03-27 14:15:05+0000", tz="Etc/GMT-0"),
                1799: pd.Timestamp("2018-03-28 01:30:21+0000", tz="Etc/GMT-0"),
                1800: pd.Timestamp("2018-03-28 13:03:30+0000", tz="Etc/GMT-0"),
                1801: pd.Timestamp("2018-03-29 01:30:21+0000", tz="Etc/GMT-0"),
                1802: pd.Timestamp("2018-03-29 08:08:16+0000", tz="Etc/GMT-0"),
                1803: pd.Timestamp("2018-03-29 13:00:21+0000", tz="Etc/GMT-0"),
            },
            "end": {
                1794: pd.Timestamp("2018-03-26 01:30:21+0000", tz="Etc/GMT-0"),
                1795: pd.Timestamp("2018-03-26 13:00:22+0000", tz="Etc/GMT-0"),
                1796: pd.Timestamp("2018-03-27 01:30:23+0000", tz="Etc/GMT-0"),
                1797: pd.Timestamp("2018-03-27 06:14:53+0000", tz="Etc/GMT-0"),
                1798: pd.Timestamp("2018-03-28 01:30:21+0000", tz="Etc/GMT-0"),
                1799: pd.Timestamp("2018-03-28 13:03:30+0000", tz="Etc/GMT-0"),
                1800: pd.Timestamp("2018-03-29 01:30:21+0000", tz="Etc/GMT-0"),
                1801: pd.Timestamp("2018-03-29 08:08:16+0000", tz="Etc/GMT-0"),
                1802: pd.Timestamp("2018-03-29 13:00:21+0000", tz="Etc/GMT-0"),
                1803: pd.Timestamp("2018-03-30 01:30:22+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                1794: pd.Timedelta("0 days 12:30:00"),
                1795: pd.Timedelta("0 days 11:30:01"),
                1796: pd.Timedelta("0 days 12:30:01"),
                1797: pd.Timedelta("0 days 04:44:30"),
                1798: pd.Timedelta("0 days 11:15:16"),
                1799: pd.Timedelta("0 days 11:33:09"),
                1800: pd.Timedelta("0 days 12:26:51"),
                1801: pd.Timedelta("0 days 06:37:55"),
                1802: pd.Timedelta("0 days 04:52:05"),
                1803: pd.Timedelta("0 days 12:30:01"),
            },
        }
    )
    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                1661: pd.Timestamp("2018-03-25 13:00:00+0000", tz="Etc/GMT-0"),
                1662: pd.Timestamp("2018-03-26 01:30:00+0000", tz="Etc/GMT-0"),
                1663: pd.Timestamp("2018-03-26 13:00:00+0000", tz="Etc/GMT-0"),
                1664: pd.Timestamp("2018-03-27 01:30:00+0000", tz="Etc/GMT-0"),
                1665: pd.Timestamp("2018-03-27 14:15:00+0000", tz="Etc/GMT-0"),
                1666: pd.Timestamp("2018-03-28 01:30:00+0000", tz="Etc/GMT-0"),
                1667: pd.Timestamp("2018-03-29 01:30:00+0000", tz="Etc/GMT-0"),
                1668: pd.Timestamp("2018-03-29 13:00:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                1661: pd.Timestamp("2018-03-26 01:30:00+0000", tz="Etc/GMT-0"),
                1662: pd.Timestamp("2018-03-26 13:00:00+0000", tz="Etc/GMT-0"),
                1663: pd.Timestamp("2018-03-27 01:30:00+0000", tz="Etc/GMT-0"),
                1664: pd.Timestamp("2018-03-27 06:14:00+0000", tz="Etc/GMT-0"),
                1665: pd.Timestamp("2018-03-28 01:30:00+0000", tz="Etc/GMT-0"),
                1666: pd.Timestamp("2018-03-29 01:30:00+0000", tz="Etc/GMT-0"),
                1667: pd.Timestamp("2018-03-29 13:00:00+0000", tz="Etc/GMT-0"),
                1668: pd.Timestamp("2018-03-30 01:30:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                1661: pd.Timedelta("0 days 12:30:00"),
                1662: pd.Timedelta("0 days 11:30:00"),
                1663: pd.Timedelta("0 days 12:30:00"),
                1664: pd.Timedelta("0 days 04:44:00"),
                1665: pd.Timedelta("0 days 11:15:00"),
                1666: pd.Timedelta("1 days 00:00:00"),
                1667: pd.Timedelta("0 days 11:30:00"),
                1668: pd.Timedelta("0 days 12:30:00"),
            },
        }
    )
    wis_periods = [
        (
            pd.Timestamp("2018-03-27 14:15:05+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2021-12-31 01:30:24+0000", tz="Etc/GMT-0"),
        ),
        (
            pd.Timestamp("2015-08-31 13:00:17+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2018-03-27 06:14:54+0000", tz="Etc/GMT-0"),
        ),
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test3",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )


def test_merge_split_case4():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                0: pd.Timestamp("2011-10-10 13:11:29+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2014-02-28 12:30:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2015-02-10 00:45:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2015-02-13 00:45:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2015-02-14 00:45:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                0: pd.Timestamp("2011-10-17 12:34:03+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2014-03-02 12:30:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2015-02-10 09:30:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2015-02-13 06:30:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2015-02-14 11:45:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                0: pd.Timedelta("6 days 23:22:34"),
                1: pd.Timedelta("2 days 00:00:00"),
                2: pd.Timedelta("0 days 08:45:00"),
                3: pd.Timedelta("0 days 05:45:00"),
                4: pd.Timedelta("0 days 11:00:00"),
            },
        }
    )
    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                0: pd.Timestamp("2011-10-10 13:00:00+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2012-03-25 11:30:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2013-03-31 01:00:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2014-02-28 12:30:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2014-03-24 00:30:00+0000", tz="Etc/GMT-0"),
                5: pd.Timestamp("2014-03-30 11:45:00+0000", tz="Etc/GMT-0"),
                6: pd.Timestamp("2015-02-10 00:45:00+0000", tz="Etc/GMT-0"),
                7: pd.Timestamp("2015-02-13 00:45:00+0000", tz="Etc/GMT-0"),
                8: pd.Timestamp("2015-02-14 00:45:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                0: pd.Timestamp("2011-10-17 12:45:00+0000", tz="Etc/GMT-0"),
                1: pd.Timestamp("2012-03-25 12:45:00+0000", tz="Etc/GMT-0"),
                2: pd.Timestamp("2013-03-31 02:00:00+0000", tz="Etc/GMT-0"),
                3: pd.Timestamp("2014-03-02 12:30:00+0000", tz="Etc/GMT-0"),
                4: pd.Timestamp("2014-03-24 01:00:00+0000", tz="Etc/GMT-0"),
                5: pd.Timestamp("2014-03-30 13:00:00+0000", tz="Etc/GMT-0"),
                6: pd.Timestamp("2015-02-10 09:30:00+0000", tz="Etc/GMT-0"),
                7: pd.Timestamp("2015-02-13 06:30:00+0000", tz="Etc/GMT-0"),
                8: pd.Timestamp("2015-02-14 11:45:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                0: pd.Timedelta("6 days 23:45:00"),
                1: pd.Timedelta("0 days 01:15:00"),
                2: pd.Timedelta("0 days 01:00:00"),
                3: pd.Timedelta("2 days 00:00:00"),
                4: pd.Timedelta("0 days 00:30:00"),
                5: pd.Timedelta("0 days 01:15:00"),
                6: pd.Timedelta("0 days 08:45:00"),
                7: pd.Timedelta("0 days 05:45:00"),
                8: pd.Timedelta("0 days 11:00:00"),
            },
        }
    )

    wis_periods = [
        (
            pd.Timestamp("2011-07-01 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2015-02-18 23:45:00+0000", tz="Etc/GMT-0"),
        )
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test4",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )


def test_merge_split_case5():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                239: pd.Timestamp("2018-03-19 23:00:00+0000", tz="Etc/GMT-0"),
                240: pd.Timestamp("2018-03-20 03:00:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                239: pd.Timestamp("2018-03-20 03:00:00+0000", tz="Etc/GMT-0"),
                240: pd.Timestamp("2018-03-20 07:00:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {239: pd.Timedelta("0 days 04:00:00"), 240: pd.Timedelta("0 days 04:00:00")},
        }
    )
    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                286: pd.Timestamp("2018-03-19 23:00:00+0000", tz="Etc/GMT-0"),
                287: pd.Timestamp("2018-03-20 03:00:00+0000", tz="Etc/GMT-0"),
                288: pd.Timestamp("2018-03-25 01:00:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                286: pd.Timestamp("2018-03-20 03:00:00+0000", tz="Etc/GMT-0"),
                287: pd.Timestamp("2018-03-20 07:00:00+0000", tz="Etc/GMT-0"),
                288: pd.Timestamp("2018-03-25 02:15:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                286: pd.Timedelta("0 days 04:00:00"),
                287: pd.Timedelta("0 days 04:00:00"),
                288: pd.Timedelta("0 days 01:15:00"),
            },
        }
    )
    wis_periods = [
        (
            pd.Timestamp("2018-03-17 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2018-03-27 11:00:00+0000", tz="Etc/GMT-0"),
        ),
        (
            pd.Timestamp("2018-03-28 07:15:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2018-03-29 23:45:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test5",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )


def test_merge_split_case6():
    df_normal_gaps = pd.DataFrame(
        data={
            "start": {
                5: pd.Timestamp("2017-05-17 06:30:00+0000", tz="Etc/GMT-0"),
                6: pd.Timestamp("2017-05-17 13:30:16+0000", tz="Etc/GMT-0"),
                7: pd.Timestamp("2017-05-18 02:45:16+0000", tz="Etc/GMT-0"),
            },
            "end": {
                5: pd.Timestamp("2017-05-17 13:30:16+0000", tz="Etc/GMT-0"),
                6: pd.Timestamp("2017-05-18 02:45:16+0000", tz="Etc/GMT-0"),
                7: pd.Timestamp("2017-05-18 13:30:20+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                5: pd.Timedelta("0 days 07:00:16"),
                6: pd.Timedelta("0 days 13:15:00"),
                7: pd.Timedelta("0 days 10:45:04"),
            },
        }
    )

    df_quarter_gaps = pd.DataFrame(
        data={
            "start": {
                44: pd.Timestamp("2016-03-27 00:45:00+0000", tz="Etc/GMT-0"),
                45: pd.Timestamp("2016-04-07 10:45:00+0000", tz="Etc/GMT-0"),
                46: pd.Timestamp("2016-10-26 12:00:00+0000", tz="Etc/GMT-0"),
            },
            "end": {
                44: pd.Timestamp("2016-03-27 02:00:00+0000", tz="Etc/GMT-0"),
                45: pd.Timestamp("2016-04-07 11:15:00+0000", tz="Etc/GMT-0"),
                46: pd.Timestamp("2016-10-26 12:30:00+0000", tz="Etc/GMT-0"),
            },
            "diff": {
                44: pd.Timedelta("0 days 01:15:00"),
                45: pd.Timedelta("0 days 00:30:00"),
                46: pd.Timedelta("0 days 00:30:00"),
            },
        }
    )

    wis_periods = [
        (
            pd.Timestamp("2011-07-01 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2015-09-30 16:00:00+0000", tz="Etc/GMT-0"),
        ),
        (
            pd.Timestamp("2018-03-27 13:15:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2021-12-31 23:45:00+0000", tz="Etc/GMT-0"),
        ),
        (
            pd.Timestamp("2015-05-28 15:45:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2018-03-27 13:15:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    # wis_periods 1 and 2 overlap but are fixed in QualifyTimeseries._validate_wis_periods()
    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test6a",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )

    # exclude the overlapping wis_period
    with pytest.raises(exceptions.CannotShiftWisPeriod):
        QualifyTimeseries.classify_subsequent_periods(
            int_loc_par="test6b",
            wis_periods=wis_periods[0:2],
            dfs_normal_gaps=[df_normal_gaps],
            dfs_quarter_gaps=[df_quarter_gaps],
        )


def test_merge_split_case7():
    df_normal_gaps = pd.DataFrame(data=None)
    df_quarter_gaps = pd.DataFrame(data=None)

    wis_periods = [
        (
            pd.Timestamp("2011-07-01 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2015-09-30 16:00:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test7",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )


def test_merge_split_case8():
    df_normal_gaps = pd.DataFrame(data=None)
    df_quarter_gaps = pd.DataFrame(data=None)

    wis_periods = [
        (
            pd.Timestamp("2011-07-01 00:00:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2015-09-30 16:00:00+0000", tz="Etc/GMT-0"),
        ),
        (
            pd.Timestamp("2018-03-27 13:15:00+0000", tz="Etc/GMT-0"),
            pd.Timestamp("2021-12-31 23:45:00+0000", tz="Etc/GMT-0"),
        ),
    ]

    QualifyTimeseries.classify_subsequent_periods(
        int_loc_par="test8",
        wis_periods=wis_periods,
        dfs_normal_gaps=[df_normal_gaps],
        dfs_quarter_gaps=[df_quarter_gaps],
    )
