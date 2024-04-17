from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.test_fews_wis import fixtures_requests
from hdsr_fewspy.tests.test_fews_wis.fixtures import fixture_api_sa_work_no_download_dir

import pytest


# silence flake8
fixture_api_sa_work_no_download_dir = fixture_api_sa_work_no_download_dir


def test_sa_time_series_stats_wrong(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir

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

    request_data = fixtures_requests.RequestTimeSeriesSingleShort
    # output_choice xml_file_in_download_dir is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_statistics(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.xml_file_in_download_dir,
        )


def test_sa_time_series_stats_2_ok_xml_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    response = api.get_time_series_statistics(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )

    assert response.status_code == 200


def test_sa_time_series_stats_1_ok_json_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleShort

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
        "lat",
        "locationId",
        "lon",
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
        "type": "instantaneous",
        "moduleInstanceId": "WerkFilter",
        "locationId": "OW433001",
        "parameterId": "H.G.0",
        "timeStep": {"unit": "nonequidistant"},
        "startDate": {"date": "2012-01-01", "time": "00:00:00"},
        "endDate": {"date": "2012-01-02", "time": "00:00:00"},
        "missVal": "-999.0",
        "stationName": "HAANWIJKERSLUIS_4330-w_Leidsche Rijn",
        "lat": "52.08992726570302",
        "lon": "4.9547458967486095",
        "x": "125362.0",
        "y": "455829.0",
        "z": "-0.18",
        "units": "mNAP",
        "valueCount": "0",
    }

    assert found_header == expected_header
