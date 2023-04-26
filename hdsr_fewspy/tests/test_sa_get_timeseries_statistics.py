from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests import fixtures_requests
from hdsr_fewspy.tests.fixtures import fixture_api_sa_no_download_dir

import pytest


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir


def test_sa_timeseries_stats_wrong(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir

    request_data = fixtures_requests.RequestTimeSeriesMulti1
    # multiple location_ids is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_statistics(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.json_response_in_memory,
        )

    request_data = fixtures_requests.RequestTimeSeriesSingle1
    # output_choice xml_file_in_download_dir is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_statistics(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.xml_file_in_download_dir,
        )


def test_sa_timeseries_stats_2_ok_xml_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle2

    response = api.get_time_series_statistics(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )

    assert response.status_code == 200


def test_sa_timeseries_stats_1_ok_json_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    response = api.get_time_series_statistics(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )

    assert response.status_code == 200
    found_ts = response.json()["timeSeries"]
    assert len(found_ts) == 1
    found_header = found_ts[0]["header"]
    found_keys = sorted(found_header.keys())
    expected_keys = [
        "endDate",
        "firstValueTime",
        "lastValueTime",
        "lat",
        "locationId",
        "lon",
        "maxValue",
        "minValue",
        "missVal",
        "moduleInstanceId",
        "parameterId",
        "startDate",
        "stationName",
        "timeStep",
        "type",
        "units",
        "valueCount",
        "x",
        "y",
        "z",
    ]
    assert found_keys == expected_keys

    expected_header = {
        "endDate": {"date": "2012-01-02", "time": "00:00:00"},
        "firstValueTime": {"date": "2012-01-01", "time": "00:15:00"},
        "lastValueTime": {"date": "2012-01-02", "time": "00:00:00"},
        "lat": "52.08992726570302",
        "locationId": "OW433001",
        "lon": "4.9547458967486095",
        "maxValue": "-0.28",
        "minValue": "-0.44",
        "missVal": "-999.0",
        "moduleInstanceId": "WerkFilter",
        "parameterId": "H.G.0",
        "startDate": {"date": "2012-01-01", "time": "00:00:00"},
        "stationName": "HAANWIJKERSLUIS_4330-w_Leidsche Rijn",
        "timeStep": {"unit": "nonequidistant"},
        "type": "instantaneous",
        "units": "mNAP",
        "valueCount": "102",
        "x": "125362.0",
        "y": "455829.0",
        "z": "-0.18",
    }

    assert found_header == expected_header
