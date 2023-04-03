from fewspy.tests.fixtures import api_mocked_fixture
from fewspy.tests.fixtures_requests import RequestData1

import pandas as pd
import responses


# silence flake8
api_mocked_fixture = api_mocked_fixture


@responses.activate
def test_mock_empty_response(api_mocked_fixture):
    request_data = RequestData1
    response_json = {"error": "bla bla bla"}
    responses.add(
        responses.GET, url=f"{api_mocked_fixture.pi_settings.base_url}timeseries/", json=response_json, status=404
    )

    ts_set_mock_empty_json = api_mocked_fixture.get_time_series(
        filter_id=request_data.filter_id,
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert isinstance(ts_set_mock_empty_json.time_series, list) and len(ts_set_mock_empty_json.time_series) == 0
    assert not ts_set_mock_empty_json.location_ids
    # TODO: why does property 'parameter_id' not exist?
    # assert not ts_set_mock_empty_json.parameter_id
    assert not ts_set_mock_empty_json.time_zone
    assert not ts_set_mock_empty_json.version


@responses.activate
def test_mock_filled_response(api_mocked_fixture):
    request_data = RequestData1

    # mock response
    url = f"{api_mocked_fixture.pi_settings.base_url}timeseries/"
    responses.add(responses.GET, url=url, json=request_data.get_expected_json(), status=200)

    ts_set_mock_filled_json = api_mocked_fixture.get_time_series(
        filter_id=request_data.filter_id,
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert isinstance(ts_set_mock_filled_json.time_series, list) and len(ts_set_mock_filled_json.time_series) == 3
    ts_1 = ts_set_mock_filled_json.time_series[0]
    ts_2 = ts_set_mock_filled_json.time_series[1]
    ts_3 = ts_set_mock_filled_json.time_series[2]

    for ts in (ts_1, ts_2, ts_3):
        first_stamp = ts.events.iloc[0]
        assert first_stamp.name == pd.Timestamp("2022-05-01 00:00:00") == pd.Timestamp(request_data.start_time)
        assert first_stamp.flag == 0.0
        assert first_stamp.value == -0.394

        last_stamp = ts.events.iloc[-1]
        assert last_stamp.name == pd.Timestamp("2022-05-02 00:00:00") == pd.Timestamp(request_data.end_time)
        assert last_stamp.flag == 0.0
        assert last_stamp.value == -0.429

    assert ts_set_mock_filled_json.location_ids == request_data.location_ids

    # TODO: why does property 'parameter_id' not exist?
    # assert ts_set_mock_filled_json.parameter_id == request_data.parameter_ids

    assert ts_set_mock_filled_json.time_zone == 0.0
    assert ts_set_mock_filled_json.version == "1.32"
