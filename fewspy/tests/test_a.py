from datetime import datetime
from fewspy.constants import BASE_DIR
from fewspy.daniel.src.fewspy.api import Api

import pandas as pd
import pytest
import requests
import responses


API_BASE_URL_TEST = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"


class RequestData1:
    filter_id = "INTERNAL-API"
    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = ["OW433001"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2022, 5, 1)
    end_time = datetime(2022, 5, 2)


@pytest.fixture(scope="session")
@responses.activate
def api_fixture():
    """Avoid mocking 2 responses in every test as instantiating Api does an additional GET request to check base url."""
    # TODO: 'timezoneid' must be also a constant
    url = f"{API_BASE_URL_TEST}timezoneid"
    responses.add(method=responses.GET, url=url, status=200)
    api = Api(base_url=API_BASE_URL_TEST)
    return api


@responses.activate
def test_mock_google_response_works():
    # mock response
    url = "https://www.google.nl/"
    response_json = {"error": "not found"}
    status_code = 404
    responses.add(method=responses.GET, url=url, json=response_json, status=status_code)

    # check response
    resp = requests.get(url=url)
    assert resp.status_code == status_code
    assert resp.json() == response_json
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_mock_filled_response(api_fixture):
    request_data = RequestData1

    import json

    file_path = BASE_DIR / "fewspy" / "tests" / "expected_json.json"
    assert file_path.is_file()
    with open(file_path.as_posix()) as src:
        response_json = json.load(src)

    # mock response
    url = f"{API_BASE_URL_TEST}timeseries"
    responses.add(responses.GET, url=url, json=response_json, status=200)

    # url = API_BASE_URL_TEST
    # response_json = {"error": "not found"}
    # status_code = 404
    # responses.add(method=responses.GET, url=url, json=response_json, status=status_code)

    ts_set_mock_filled_json = api_fixture.get_time_series(
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


@responses.activate
def test_mock_empty_response(api_fixture):
    request_data = RequestData1
    response_json = {"error": "bla bla bla"}
    responses.add(responses.GET, url=f"{API_BASE_URL_TEST}timeseries", json=response_json, status=404)

    ts_set_mock_empty_json = api_fixture.get_time_series(
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
