from fewspy.constants.choices import OutputChoices
from fewspy.tests import fixtures_requests
from fewspy.tests.fixtures import fixture_api_sa_json_download
from fewspy.tests.fixtures import fixture_api_sa_json_memory

import pytest


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_json_memory
fixture_api_sa_json_download = fixture_api_sa_json_download


def test_sa_single_timeseries_wrong_requests(fixture_api_sa_json_memory):
    pass


def test_sa_single_timeseries_ok_requests(fixture_api_sa_json_memory):
    assert fixture_api_sa_json_memory.output_choice == OutputChoices.json_response_in_memory
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = fixture_api_sa_json_memory.get_time_series(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert len(responses) == 1
    response = responses[0]
    assert response.status_code == 200
    json_found = response.json()
    json_expected = request_data.get_expected_json()
    assert json_found == json_expected
