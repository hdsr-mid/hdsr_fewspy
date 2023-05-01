from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.converters.xml_to_python_obj import parse
from hdsr_fewspy.tests import fixtures_requests
from hdsr_fewspy.tests.fixtures import fixture_api_sa_no_download_dir
from hdsr_fewspy.tests.fixtures import fixture_api_sa_with_download_dir

import pandas as pd
import pytest


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir
fixture_api_sa_with_download_dir = fixture_api_sa_with_download_dir


def test_sa_single_timeseries_1_wrong(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir

    request_data = fixtures_requests.RequestTimeSeriesMulti1
    # multiple location_ids is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_single(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.json_response_in_memory,
        )

    request_data = fixtures_requests.RequestTimeSeriesSingle1
    # output_choice xml_file_in_download_dir is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_single(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.xml_file_in_download_dir,
        )


def test_sa_single_timeseries_1_ok_json_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )

    mapper_jsons_expected = request_data.get_expected_jsons()
    assert len(mapper_jsons_expected.keys()) == len(responses) == 1
    for response_found, expected_json_key in zip(responses, mapper_jsons_expected.keys()):
        assert response_found.status_code == 200
        json_found = response_found.json()
        json_expected = mapper_jsons_expected[expected_json_key]
        assert json_found == json_expected


def test_sa_single_timeseries_1_ok_xml_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )

    mapper_xmls_expected = request_data.get_expected_xmls()
    assert len(mapper_xmls_expected.keys()) == len(responses) == 1
    for response_found, expected_xml_key in zip(responses, mapper_xmls_expected.keys()):
        assert response_found.status_code == 200

        xml_expected = mapper_xmls_expected[expected_xml_key]
        expected_header = xml_expected.TimeSeries.series.header
        expected_events = xml_expected.TimeSeries.series.event
        expected_unit = expected_header.timeStep._attributes["unit"]

        found = parse(response_found.text)
        found_header = found.TimeSeries.series.header
        found_events = found.TimeSeries.series.event
        found_unit = found_header.timeStep._attributes["unit"]

        assert found_unit == expected_unit == "nonequidistant"
        assert len(found_events) == len(expected_events) == 102
        assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"] == "2012-01-01"
        assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"] == "2012-01-02"


def test_sa_single_timeseries_1_ok_df_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle1

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
    )
    mapper_dfs_expected = request_data.get_expected_dfs_from_csvs()
    assert len(mapper_dfs_expected.keys()) == 1
    first_key = next(iter(mapper_dfs_expected))
    df_expected = mapper_dfs_expected[first_key]
    df_expected.set_index("datetime", inplace=True)

    df_found.set_index(pd.to_datetime(df_found.index), inplace=True)
    df_expected.set_index(pd.to_datetime(df_expected.index), inplace=True)
    pd.testing.assert_frame_equal(left=df_found, right=df_expected, check_index_type=False)


def test_sa_single_timeseries_2_ok_json_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle2

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )
    assert len(responses) == 11


def test_sa_single_timeseries_2_ok_xml_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle2

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )
    assert len(responses) == 11


def test_sa_single_timeseries_2_ok_df_memory(fixture_api_sa_no_download_dir):
    api = fixture_api_sa_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingle2

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
    )
    assert len(df_found) == 199251
