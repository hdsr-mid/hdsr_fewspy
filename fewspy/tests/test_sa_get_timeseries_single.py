from fewspy.constants.choices import OutputChoices
from fewspy.response_converters.xml_to_python_obj import parse
from fewspy.tests import fixtures_requests
from fewspy.tests.fixtures import fixture_api_sa_no_download_dir
from fewspy.tests.fixtures import fixture_api_sa_with_download_dir


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_no_download_dir
fixture_api_sa_xml_download = fixture_api_sa_with_download_dir


def test_sa_single_timeseries_ok_json_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )

    jsons_expected = request_data.get_expected_jsons()
    assert len(jsons_expected.keys()) == len(responses) == 1
    for response_found, expected_json_key in zip(responses, jsons_expected.keys()):
        assert response_found.status_code == 200
        json_found = response_found.json()
        json_expected = jsons_expected[expected_json_key]
        assert json_found == json_expected


def test_sa_single_timeseries_ok_xml_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )

    xmls_expected = request_data.get_expected_xmls()
    assert len(xmls_expected.keys()) == len(responses) == 1
    for response_found, expected_xml_key in zip(responses, xmls_expected.keys()):
        assert response_found.status_code == 200

        xml_expected = xmls_expected[expected_xml_key]
        expected_header = xml_expected.TimeSeries.series.header
        expected_events = xml_expected.TimeSeries.series.event

        found = parse(response_found.text)
        found_header = found.TimeSeries.series.header
        found_events = found.TimeSeries.series.event

        assert (
            found_header.timeStep._attributes["unit"]
            == expected_header.timeStep._attributes["unit"]
            == "nonequidistant"
        )
        assert len(found_events) == len(expected_events) == 102
        assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"] == "2012-01-01"
        assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"] == "2012-01-02"
