from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.converters.utils import fews_date_str_to_datetime
from hdsr_fewspy.converters.xml_to_python_obj import parse
from hdsr_fewspy.tests import fixtures_requests
from hdsr_fewspy.tests.fixtures import fixture_api_sa_raw_no_download_dir
from hdsr_fewspy.tests.fixtures import fixture_api_sa_validated_no_download_dir
from hdsr_fewspy.tests.fixtures import fixture_api_sa_work_no_download_dir
from hdsr_fewspy.tests.fixtures import fixture_api_sa_work_with_download_dir

import pandas as pd
import pytest


# silence flake8
fixture_api_sa_work_no_download_dir = fixture_api_sa_work_no_download_dir
fixture_api_sa_work_with_download_dir = fixture_api_sa_work_with_download_dir
fixture_api_sa_raw_no_download_dir = fixture_api_sa_raw_no_download_dir
fixture_api_sa_validated_no_download_dir = fixture_api_sa_validated_no_download_dir


def test_sa_single_ts_wrong(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir

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

    request_data = fixtures_requests.RequestTimeSeriesSingleShort
    # output_choice xml_file_in_download_dir is not possible
    with pytest.raises(AssertionError):
        api.get_time_series_single(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.xml_file_in_download_dir,
        )

    request_data = fixtures_requests.RequestTimeSeriesSingleShort
    # wrong format start-time string '2012-Jan-01'
    try:
        api.get_time_series_single(
            location_id=request_data.location_ids,
            parameter_id=request_data.parameter_ids,
            start_time=request_data.start_time.strftime("%Y-%h-%d"),
            end_time=request_data.end_time,
            output_choice=OutputChoices.xml_file_in_download_dir,
        )
    except Exception as err:
        assert err.args[0] == "Could not convert str 2012-Jan-01 to datetime using format '%Y-%m-%dT%H:%M:%SZ'"


def test_sa_single_ts_nan(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    responses = api.get_time_series_single(
        location_id="OW123456789",  # location does not exist
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )
    assert not responses


def test_sa_single_ts_short_ok_json_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleShort

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


def test_sa_single_ts_short_time_as_strings(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleShort

    start_time_string = request_data.start_time.strftime(TimeZoneChoices.date_string_format())
    assert start_time_string == "2012-01-01T00:00:00Z"
    assert fews_date_str_to_datetime(fews_date_str=start_time_string) == request_data.start_time

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=start_time_string,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )
    assert len(responses) == 1


def test_sa_single_ts_short_ok_xml_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleShort

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
        try:
            expected_events = xml_expected.TimeSeries.series.event
        except AttributeError:
            expected_events = []
        expected_unit = expected_header.timeStep._attributes["unit"]

        found = parse(response_found.text)
        found_header = found.TimeSeries.series.header
        try:
            found_events = found.TimeSeries.series.event
        except AttributeError:
            found_events = []
        found_unit = found_header.timeStep._attributes["unit"]

        assert found_unit == expected_unit == "nonequidistant"
        assert len(found_events) == len(expected_events)  # == 102
        # assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"] == "2012-01-01"
        # assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"] == "2012-01-02"


def test_sa_single_ts_short_ok_df_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleShort

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


def test_sa_single_ts_long_ok_json_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_response_in_memory,
    )
    assert len(responses) == 1  # 4
    assert not api.request_settings.updated_request_period  # == pd.Timedelta(days=365, hours=6, minutes=0, seconds=0)


def test_sa_single_ts_long_ok_xml_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    responses = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_response_in_memory,
    )
    assert len(responses) == 1  # 4
    assert api.request_settings.updated_request_period is None  # pd.Timedelta(days=365, hours=6, minutes=0, seconds=0)


def test_sa_single_ts_long_ok_df_memory(fixture_api_sa_work_no_download_dir):
    api = fixture_api_sa_work_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
    )
    assert len(df_found) == 0  # 199252
    assert api.request_settings.updated_request_period is None  # pd.Timedelta(days=365, hours=6, minutes=0, seconds=0)


def test_sa_single_raw_ts_long_ok_df_memory(fixture_api_sa_raw_no_download_dir):
    api = fixture_api_sa_raw_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
    )
    assert len(df_found) == 0
    assert api.request_settings.updated_request_period is None


def test_sa_single_validated_ts_long_ok_df_memory(fixture_api_sa_validated_no_download_dir):
    api = fixture_api_sa_validated_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
    )
    assert sorted(df_found.columns) == ["flag", "location_id", "parameter_id", "value"]
    assert len(df_found) == 194444
    assert api.request_settings.updated_request_period == pd.Timedelta(days=365, hours=6, minutes=0, seconds=0)


def test_sa_single_validated_ts_long_ok_df_memory_all_fields(fixture_api_sa_validated_no_download_dir):
    api = fixture_api_sa_validated_no_download_dir
    request_data = fixtures_requests.RequestTimeSeriesSingleLong

    df_found = api.get_time_series_single(
        location_id=request_data.location_ids,
        parameter_id=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.pandas_dataframe_in_memory,
        only_value_and_flag=False,
    )
    assert sorted(df_found.columns) == ["date", "flag", "location_id", "parameter_id", "time", "value"]
    assert len(df_found) == 194444
    assert api.request_settings.updated_request_period == pd.Timedelta(days=365, hours=6, minutes=0, seconds=0)
