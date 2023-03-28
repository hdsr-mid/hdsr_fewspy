from datetime import datetime
from fewspy.constants.paths import BASE_DIR
from fewspy.tests.fixtures import api_sa_fixture

import json
import responses


# silence flake8
api_sa_fixture = api_sa_fixture


class RequestData1:
    filter_id = "INTERNAL-API"
    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = ["OW433001"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2022, 5, 1)
    end_time = datetime(2022, 5, 2)

    @classmethod
    def get_expected_json(cls):
        file_path = BASE_DIR / "fewspy" / "tests" / "data" / "input" / "expected_json.json"
        assert file_path.is_file()
        with open(file_path.as_posix()) as src:
            response_json = json.load(src)
        return response_json


def test_mock_empty_response(api_sa_fixture):
    request_data = RequestData1
    response_json = {"error": "bla bla bla"}
    responses.add(responses.GET, url=f"{api_sa_fixture.base_url}timeseries", json=response_json, status=404)

    ts_set_mock_empty_json = api_sa_fixture.get_time_series(
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
