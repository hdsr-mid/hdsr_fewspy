from fewspy.tests.fixtures import api_sa_fixture
from fewspy.tests.fixtures_requests import RequestData1
from fewspy.tests.fixtures_requests import RequestData2

import pandas as pd
import pytest


# silence flake8
api_sa_fixture = api_sa_fixture


def test_sa_wrong_request1(api_sa_fixture):
    """Arguments start and end are required for get_timeseries."""
    request_data = RequestData1

    # args start is required for get_timeseries
    with pytest.raises(TypeError):  # get_time_series() missing 1 required positional argument: 'start_time'
        api_sa_fixture.get_time_series(
            filter_id=request_data.filter_id,
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            # skip start: start_time=request_data.start_time
            end_time=request_data.end_time,
        )
    # args end is required for get_timeseries
    with pytest.raises(Exception):  # get_time_series() missing 1 required positional argument: 'end_time'
        api_sa_fixture.get_time_series(
            filter_id=request_data.filter_id,
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.start_time
            # skip end: end_time=request_data.end_time,
        )


def test_sa_wrong_request2(api_sa_fixture):
    """Arguments start and end must be valid."""
    request_data = RequestData1
    with pytest.raises(AssertionError):
        api_sa_fixture.get_time_series(
            filter_id=request_data.filter_id,
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.end_time,  # <- flipped start with end
            end_time=request_data.start_time,  # <- flipped end with start
        )


def test_sa_ok_request1(api_sa_fixture):
    request_data = RequestData1

    ts_set_json = api_sa_fixture.get_time_series(
        filter_id=request_data.filter_id,
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert isinstance(ts_set_json.time_series, list) and len(ts_set_json.time_series) == 3
    ts_1 = ts_set_json.time_series[0]
    ts_2 = ts_set_json.time_series[1]
    ts_3 = ts_set_json.time_series[2]

    for ts in (ts_1, ts_2, ts_3):
        first_stamp = ts.events.iloc[0]
        assert first_stamp.name == pd.Timestamp("2022-05-01 00:00:00") == pd.Timestamp(request_data.start_time)
        assert first_stamp.flag == 0.0
        assert first_stamp.value == -0.394

        last_stamp = ts.events.iloc[-1]
        assert last_stamp.name == pd.Timestamp("2022-05-02 00:00:00") == pd.Timestamp(request_data.end_time)
        assert last_stamp.flag == 0.0
        assert last_stamp.value == -0.429

    assert ts_set_json.location_ids == request_data.location_ids

    # TODO: why does property 'parameter_id' not exist?
    # assert ts_set_json.parameter_id == request_data.parameter_ids

    assert ts_set_json.time_zone == 0.0
    assert ts_set_json.version == "1.32"


def test_sa_ok_request2(api_sa_fixture):
    request_data = RequestData2

    timeseries_response = api_sa_fixture.get_time_series(
        filter_id=request_data.filter_id,
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )

    print(1)
