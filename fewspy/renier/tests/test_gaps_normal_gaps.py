from gapfinder.constants.columns_and_keys import RedisOuterKeys
from gapfinder.tests.fixtures import redis_test_db
from gapfinder.tests.fixtures import ts_analyser_fixture
from hdsr_wis_config_reader.idmappings.columns import IdMapCols

import pandas as pd


# silence flake8
manager_2_ts_analyser_2h_3_per_45min = ts_analyser_fixture
redis_test_db = redis_test_db


def test_normal_gaps_df(ts_analyser_fixture):
    df_gaps = ts_analyser_fixture.normal_gap_analyser.df_gaps
    expected_df = pd.DataFrame(
        {
            "start": {
                0: pd.Timestamp("2011-09-29 05:00:00+0000", tz="UTC"),
                1: pd.Timestamp("2011-09-29 08:00:00+0000", tz="UTC"),
            },
            "end": {
                0: pd.Timestamp("2011-09-29 07:01:00+0000", tz="UTC"),
                1: pd.Timestamp("2011-09-29 20:00:00+0000", tz="UTC"),
            },
            "diff": {0: pd.Timedelta("0 days 02:01:00"), 1: pd.Timedelta("0 days 12:00:00")},
        }
    )
    pd.testing.assert_frame_equal(left=df_gaps, right=expected_df)


def test_normal_gaps_missing_values(ts_analyser_fixture):
    # normal_gap_analyser deletes the constants.PI_MISSING_VALUE-999 before analyses
    assert ts_analyser_fixture.nr_missing_values == 2
    assert ts_analyser_fixture.normal_gap_analyser.nr_missing_values_discarded == 2
    assert ts_analyser_fixture.nr_unwanted_flags == 1
    assert ts_analyser_fixture.normal_gap_analyser.nr_unwanted_flags_discarded == 1


def test_normal_gaps_histogram_hours(ts_analyser_fixture):
    histogram = ts_analyser_fixture.normal_gap_analyser.histogram_hours
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 2

    # 1 gap with length between 2 and 3 hours
    assert histogram.index[0] == pd.Interval(2.0, 3.0, closed="right")
    assert histogram.iloc[0] == 1

    # 1 gap with length between 5 and 6 hours
    assert histogram.index[1] == pd.Interval(11.0, 12.0, closed="right")
    assert histogram.iloc[1] == 1


def test_normal_gaps_histogram_days(ts_analyser_fixture):
    histogram = ts_analyser_fixture.normal_gap_analyser.histogram_days
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 2

    # 2 gaps with length between 0 and 1 days
    assert histogram.index[0] == pd.Interval(-0.001, 1.0, closed="right")
    assert histogram.iloc[0] == 2


def test_normal_gaps_histogram_weeks(ts_analyser_fixture):
    histogram = ts_analyser_fixture.normal_gap_analyser.histogram_weeks
    assert isinstance(histogram, pd.Series)
    assert histogram.sum() == 2

    # 2 gaps with length between 0 and 1 weeks
    assert histogram.index[0] == pd.Interval(-0.001, 1.0, closed="right")
    assert histogram.iloc[0] == 2


def test_normal_gaps_save_in_and_read_from_redis(ts_analyser_fixture, redis_test_db):
    df_gaps = ts_analyser_fixture.normal_gap_analyser.df_gaps
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
    outer_key = RedisOuterKeys.key_normal_gaps(row=row)
    assert outer_key == "110_HB1_OW211001_H.G.0:normal-gaps"
    redis_test_db.add_df_normal_gaps(outer_key=outer_key, df_gaps=df_gaps)
    df_redis_out = redis_test_db.get_df_normal_gaps(outer_key=outer_key)
    pd.testing.assert_frame_equal(left=df_gaps, right=df_redis_out)
