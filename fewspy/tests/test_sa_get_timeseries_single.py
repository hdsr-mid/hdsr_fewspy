from fewspy.constants.choices import OutputChoices
from fewspy.response_converters.xml_to_python_obj import parse
from fewspy.response_converters.xml_to_python_obj import parse_raw
from fewspy.tests import fixtures_requests
from fewspy.tests.fixtures import fixture_api_sa_json_download
from fewspy.tests.fixtures import fixture_api_sa_json_memory
from fewspy.tests.fixtures import fixture_api_sa_xml_download
from fewspy.tests.fixtures import fixture_api_sa_xml_memory
from xml.etree import ElementTree


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_json_memory
fixture_api_sa_json_download = fixture_api_sa_json_download
fixture_api_sa_xml_memory = fixture_api_sa_xml_memory
fixture_api_sa_xml_download = fixture_api_sa_xml_download


def test_sa_single_timeseries_json_ok(fixture_api_sa_json_memory):
    api = fixture_api_sa_json_memory
    assert api.default_output_choice == OutputChoices.json_response_in_memory
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert len(responses) == 1
    response = responses[0]
    assert response.status_code == 200
    json_found = response.json()
    json_expected = request_data.get_expected_json()
    assert json_found == json_expected


def test_sa_single_timeseries_xml_ok(fixture_api_sa_xml_memory):
    api = fixture_api_sa_xml_memory
    assert api.default_output_choice == OutputChoices.xml_response_in_memory
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert len(responses) == 1
    response = responses[0]
    assert response.status_code == 200

    # with open(request_data.file_path_expected_xml().as_posix(), 'w') as f:
    #     f.write(response.text)

    expected = parse(filename=request_data.file_path_expected_xml().as_posix())
    found = parse_raw(xml=response.text)

    print(1)

    # renier fix deze sheit
