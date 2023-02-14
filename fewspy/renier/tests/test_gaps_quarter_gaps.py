from gapfinder.constants.columns_and_keys import RedisOuterKeys
from gapfinder.tests.fixtures import redis_test_db
from gapfinder.tests.fixtures import ts_analyser_fixture
from hdsr_wis_config_reader.idmappings.columns import IdMapCols

import pandas as pd


# silence flake8
ts_analyser_fixture = ts_analyser_fixture
redis_test_db = redis_test_db

expected_df_gaps = pd.DataFrame(
    {
        "start": {
            0: pd.Timestamp("2011-09-29 00:00:00+0000", tz="UTC"),
            1: pd.Timestamp("2011-09-29 02:15:00+0000", tz="UTC"),
            2: pd.Timestamp("2011-09-29 03:00:00+0000", tz="UTC"),
            3: pd.Timestamp("2011-09-29 05:00:00+0000", tz="UTC"),
            4: pd.Timestamp("2011-09-29 08:00:00+0000", tz="UTC"),
        },
        "end": {
            0: pd.Timestamp("2011-09-29 00:30:00+0000", tz="UTC"),
            1: pd.Timestamp("2011-09-29 03:00:00+0000", tz="UTC"),
            2: pd.Timestamp("2011-09-29 05:00:00+0000", tz="UTC"),
            3: pd.Timestamp("2011-09-29 08:00:00+0000", tz="UTC"),
            4: pd.Timestamp("2011-09-29 20:00:00+0000", tz="UTC"),
        },
        "diff": {
            0: pd.Timedelta("0 days 00:30:00"),
            1: pd.Timedelta("0 days 00:45:00"),
            2: pd.Timedelta("0 days 02:00:00"),
            3: pd.Timedelta("0 days 03:00:00"),
            4: pd.Timedelta("0 days 12:00:00"),
        },
    }
)


def test_quarter_gaps_df(ts_analyser_fixture):
    df_gaps = ts_analyser_fixture.quarter_gap_analyser.df_gaps
    pd.testing.assert_frame_equal(left=df_gaps, right=expected_df_gaps)


def test_quarter_gaps_missing_values(ts_analyser_fixture):
    assert ts_analyser_fixture.nr_missing_values == 2
    assert ts_analyser_fixture.quarter_gap_analyser.nr_missing_values_discarded == 2
    assert ts_analyser_fixture.nr_unwanted_flags == 1
    assert ts_analyser_fixture.quarter_gap_analyser.nr_unwanted_flags_discarded == 1


def test_quarter_gaps_histogram_hours(ts_analyser_fixture):
    histogram = ts_analyser_fixture.quarter_gap_analyser.histogram_hours
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 5

    # 2 gaps with length between 0 and 1 hour
    assert histogram.index[0] == pd.Interval(-0.001, 1.0, closed="right")
    assert histogram.iloc[0] == 2

    # 1 gap with length between 2 and 3 hours
    assert histogram.index[1] == pd.Interval(2.0, 3.0, closed="right")
    assert histogram.iloc[1] == 1

    # 1 gap with length between 11 and 12 hours
    assert histogram.index[2] == pd.Interval(11.0, 12.0, closed="right")
    assert histogram.iloc[2] == 1

    # 1 gap with length between 1 and 2 hours
    assert histogram.index[3] == pd.Interval(1.0, 2.0, closed="right")
    assert histogram.iloc[3] == 1


def test_quarter_gaps_histogram_days(ts_analyser_fixture):
    histogram = ts_analyser_fixture.quarter_gap_analyser.histogram_days
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 5

    # 5 gaps with length between 0 and 1 day
    assert histogram.index[0] == pd.Interval(-0.001, 1.0, closed="right")
    assert histogram.iloc[0] == 5


def test_quarter_gaps_histogram_weeks(ts_analyser_fixture):
    histogram = ts_analyser_fixture.quarter_gap_analyser.histogram_weeks
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 5

    # 5 gaps with length between 0 and 1 week
    assert histogram.index[0] == pd.Interval(-0.001, 1.0, closed="right")
    assert histogram.iloc[0] == 5


def test_quarter_gaps_save_in_and_read_from_redis(ts_analyser_fixture, redis_test_db):
    df_gaps = ts_analyser_fixture.quarter_gap_analyser.df_gaps
    row = pd.Series(
        data={
            "series": "110_HB1",
            "start": "2011-02-26 23:59:59",
            "end": "2011-03-07 23:59:59",
            "filename_start": "HDSR_CAW_historie_201109191148",
            "filename_end": "HDSR_CAW_historie_201109191148",
            IdMapCols.ex_loc: "110",
            IdMapCols.ex_par: "HB1",
            IdMapCols.int_loc: "OW211001",
            IdMapCols.int_par: "H.G.0",
            "idmap_source": "IdOPVLWATER",
        }
    )
    outer_key = RedisOuterKeys.key_quarter_gaps(row=row)
    assert outer_key == "110_HB1_OW211001_H.G.0:quarter-gaps"
    redis_test_db.add_df_quarter_gaps(outer_key=outer_key, df_gaps=df_gaps)
    df_redis_out = redis_test_db.get_df_quarter_gaps(outer_key=outer_key)
    pd.testing.assert_frame_equal(left=df_gaps, right=df_redis_out)
