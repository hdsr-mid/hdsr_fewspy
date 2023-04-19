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

    # create new expected file?
    # with open(request_data.file_path_expected_xml().as_posix(), 'w') as f:
    #     f.write(response.text)

    expected = parse(filename=request_data.file_path_expected_xml().as_posix())
    found = parse(response.text)

    expected_header = expected.TimeSeries.series.header
    found_header = found.TimeSeries.series.header
    assert found_header.timeStep._attributes["unit"] == expected_header.timeStep._attributes["unit"] == "nonequidistant"

    expected_events = expected.TimeSeries.series.event
    found_events = found.TimeSeries.series.event
    assert len(found_events) == len(expected_events) == 102
    assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"] == "2012-01-01"
    assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"] == "2012-01-02"
