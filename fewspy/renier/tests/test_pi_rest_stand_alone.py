from gapfinder.hdsr_hkvfewspy.pi_rest import TimeSeriesCols
from gapfinder.tests._expected_df_filters import expected_filters_sa
from gapfinder.tests.fixtures import loc_date_query_parameters_kw100111_f0
from gapfinder.tests.fixtures import loc_date_query_parameters_ow100102_hg0
from gapfinder.tests.fixtures import stand_alone_pi_rest

import pandas as pd


# silence flake8
loc_date_query_parameters_kw100111_f0 = loc_date_query_parameters_kw100111_f0
loc_date_query_parameters_ow100102_hg0 = loc_date_query_parameters_ow100102_hg0
stand_alone_pi_rest = stand_alone_pi_rest

expected_columns_hkv_ts = [
    "flag",
    "locationId",
    "moduleInstanceId",
    "parameterId",
    "qualifierId",
    "stationName",
    "units",
    "value",
]


def test_sa_filters(stand_alone_pi_rest):
    """getFilters() return all filters regardless of module_instance_id and filter_id."""
    df_filters = stand_alone_pi_rest.hkv_pi.getFilters()
    pd.testing.assert_frame_equal(left=df_filters, right=expected_filters_sa)


def test_ts_stand_alone_simple_ow(loc_date_query_parameters_ow100102_hg0, stand_alone_pi_rest):
    query_parameters_dict = stand_alone_pi_rest._get_default_query_parameters()
    for key, value in loc_date_query_parameters_ow100102_hg0.items():
        query_parameters_dict[key] = value
    assert query_parameters_dict["useDisplayUnits"] is False

    int_loc = query_parameters_dict["locationIds"][0]
    int_par = query_parameters_dict["parameterIds"][0]
    start = pd.Timestamp(query_parameters_dict["startTime"])
    end = pd.Timestamp(query_parameters_dict["endTime"])

    df_hdsr = stand_alone_pi_rest.get_time_series_hdsr(int_loc=int_loc, int_par=int_par, start=start, end=end)
    assert len(df_hdsr) == 154
    assert sorted(df_hdsr.columns) == sorted(TimeSeriesCols.get_all())

    df_hkv = stand_alone_pi_rest.get_time_series_hkv(int_loc=int_loc, int_par=int_par, start=start, end=end)
    assert len(df_hkv) == 154
    assert sorted(df_hkv.columns) == sorted(expected_columns_hkv_ts)


def test_ts_stand_alone_simple_non_ow(loc_date_query_parameters_kw100111_f0, stand_alone_pi_rest):
    query_parameters_dict = stand_alone_pi_rest._get_default_query_parameters()
    for key, value in loc_date_query_parameters_kw100111_f0.items():
        query_parameters_dict[key] = value
    assert query_parameters_dict["useDisplayUnits"] is False

    int_loc = query_parameters_dict["locationIds"][0]
    int_par = query_parameters_dict["parameterIds"][0]
    start = pd.Timestamp(query_parameters_dict["startTime"])
    end = pd.Timestamp(query_parameters_dict["endTime"])

    df_hdsr = stand_alone_pi_rest.get_time_series_hdsr(int_loc=int_loc, int_par=int_par, start=start, end=end)
    assert len(df_hdsr) == 145
    assert sorted(df_hdsr.columns) == sorted(TimeSeriesCols.get_all())

    df_hkv = stand_alone_pi_rest.get_time_series_hkv(int_loc=int_loc, int_par=int_par, start=start, end=end)
    assert len(df_hkv) == 145
    assert sorted(df_hkv.columns) == sorted(expected_columns_hkv_ts)


def test_ts_stand_alone_value_count_ow(loc_date_query_parameters_ow100102_hg0, stand_alone_pi_rest):
    query_parameters_dict = stand_alone_pi_rest._get_default_query_parameters()
    for key, value in loc_date_query_parameters_ow100102_hg0.items():
        query_parameters_dict[key] = value
    assert query_parameters_dict["useDisplayUnits"] is False

    int_loc = query_parameters_dict["locationIds"][0]
    int_par = query_parameters_dict["parameterIds"][0]
    start = pd.Timestamp(query_parameters_dict["startTime"])
    end = pd.Timestamp(query_parameters_dict["endTime"])

    value_count = stand_alone_pi_rest.get_time_series_value_count(
        int_loc=int_loc, int_par=int_par, start=start, end=end
    )
    assert value_count == 154


def test_ts_stand_alone_value_count_non_ow(loc_date_query_parameters_kw100111_f0, stand_alone_pi_rest):
    query_parameters_dict = stand_alone_pi_rest._get_default_query_parameters()
    for key, value in loc_date_query_parameters_kw100111_f0.items():
        query_parameters_dict[key] = value
    assert query_parameters_dict["useDisplayUnits"] is False

    int_loc = query_parameters_dict["locationIds"][0]
    int_par = query_parameters_dict["parameterIds"][0]
    start = pd.Timestamp(query_parameters_dict["startTime"])
    end = pd.Timestamp(query_parameters_dict["endTime"])

    value_count = stand_alone_pi_rest.get_time_series_value_count(
        int_loc=int_loc, int_par=int_par, start=start, end=end
    )
    assert value_count == 145
