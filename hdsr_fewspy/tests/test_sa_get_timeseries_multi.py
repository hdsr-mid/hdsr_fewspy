from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.converters.xml_to_python_obj import parse
from hdsr_fewspy.tests import fixtures_requests
from hdsr_fewspy.tests.fixtures import fixture_api_sa_no_download_dir
from hdsr_fewspy.tests.fixtures import fixture_api_sa_with_download_dir

import json
import pandas as pd
import pytest


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir
fixture_api_sa_with_download_dir = fixture_api_sa_with_download_dir


def test_sa_multi_timeseries_wrong(fixture_api_sa_with_download_dir):
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    # start_time is skipped
    with pytest.raises(TypeError):
        api.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            # start_time: start_time=request_data.start_time
            end_time=request_data.end_time,
            output_choice=OutputChoices.json_file_in_download_dir,
        )

    # end_time is skipped
    with pytest.raises(TypeError):  # get_time_series() missing 1 required positional argument: 'end_time'
        api.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.start_time,
            # end_time: end_time=request_data.end_time,
            output_choice=OutputChoices.json_file_in_download_dir,
        )

    # flipped start_time and end_time
    try:
        api.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.end_time,  # <- flipped start_time with end_time
            end_time=request_data.start_time,  # <- flipped end_time with start_time
            output_choice=OutputChoices.json_file_in_download_dir,
        )
    except AssertionError as err:
        assert err.args[0] == f"start_time {request_data.end_time} must be before end_time {request_data.start_time}"

    # OutputChoices json_response_in_memory is invalid for get_time_series_multi()
    try:
        api.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
            output_choice=OutputChoices.json_response_in_memory,
        )
    except Exception as err:
        msg = (
            "invalid output_choice 'json_response_in_memory'. GetTimeSeriesMulti has valid_output_choices "
            "['xml_file_in_download_dir', 'json_file_in_download_dir', 'csv_file_in_download_dir']. See earlier "
            "logging why we use GetTimeSeriesMulti."
        )
        assert err.args[0] == msg


def test_sa_multi_timeseries_1_ok_json_download(fixture_api_sa_with_download_dir):
    """OutputChoices.json_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_file_in_download_dir,
    )
    assert len(all_file_paths) == 2
    assert all_file_paths[0].name == "gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z_0.json"
    assert all_file_paths[1].name == "gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z_0.json"

    mapper_expected_jsons = request_data.get_expected_jsons()
    for downloaded_file in all_file_paths:
        with open(downloaded_file.as_posix()) as src:
            found_json = json.load(src)
        expected_json = mapper_expected_jsons[downloaded_file.stem]
        assert found_json == expected_json


def test_sa_multi_timeseries_1_ok_xml_download(fixture_api_sa_with_download_dir):
    """OutputChoices.xml_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_file_in_download_dir,
    )
    assert len(all_file_paths) == 2
    assert all_file_paths[0].name == "gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z_0.xml"
    assert all_file_paths[1].name == "gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z_0.xml"

    mapper_expected_xmls = request_data.get_expected_xmls()
    for downloaded_file in all_file_paths:
        found = parse(downloaded_file.as_posix())
        found_header = found.TimeSeries.series.header
        found_events = found.TimeSeries.series.event

        expected = mapper_expected_xmls[downloaded_file.stem]
        expected_header = expected.TimeSeries.series.header
        expected_events = expected.TimeSeries.series.event

        assert found_header.timeStep._attributes["unit"] == expected_header.timeStep._attributes["unit"]
        assert len(found_events) == len(expected_events)
        assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"]
        assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"]


def test_sa_multi_timeseries_1_ok_csv_download(fixture_api_sa_with_download_dir):
    """OutputChoices.csv_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.csv_file_in_download_dir,
    )
    assert len(all_file_paths) == 2
    assert all_file_paths[0].name == "gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z.csv"
    assert all_file_paths[1].name == "gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z.csv"

    mapper_csv_expected = request_data.get_expected_dfs_from_csvs()
    for downloaded_file in all_file_paths:
        df_found = pd.read_csv(filepath_or_buffer=downloaded_file, sep=",")
        df_expected = mapper_csv_expected[downloaded_file.stem]
        pd.testing.assert_frame_equal(left=df_found, right=df_expected)


def test_sa_multi_timeseries_2_ok_json_download(fixture_api_sa_with_download_dir):
    """OutputChoices.json_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti2

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.json_file_in_download_dir,
    )
    assert len(all_file_paths) == 4
    assert all_file_paths[0].name == "gettimeseriesmulti_kw215712_qby_20050101t000000z_20050102t000000z_0.json"
    assert all_file_paths[1].name == "gettimeseriesmulti_kw215712_ddy_20050101t000000z_20050102t000000z_0.json"
    assert all_file_paths[2].name == "gettimeseriesmulti_kw322613_qby_20050101t000000z_20050102t000000z_0.json"
    assert all_file_paths[3].name == "gettimeseriesmulti_kw322613_ddy_20050101t000000z_20050102t000000z_0.json"

    mapper_expected_jsons = request_data.get_expected_jsons()
    for downloaded_file in all_file_paths:
        with open(downloaded_file.as_posix()) as src:
            found_json = json.load(src)
        expected_json = mapper_expected_jsons[downloaded_file.stem]
        assert found_json == expected_json


def test_sa_multi_time_series_2_ok_xml_download(fixture_api_sa_with_download_dir):
    """OutputChoices.xml_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti2

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.xml_file_in_download_dir,
    )
    assert len(all_file_paths) == 3

    mapper_expected_xmls = request_data.get_expected_xmls()
    for downloaded_file in all_file_paths:
        found = parse(downloaded_file.as_posix())
        found_header = found.TimeSeries.series.header
        found_events = found.TimeSeries.series.event

        expected = mapper_expected_xmls[downloaded_file.stem]
        expected_header = expected.TimeSeries.series.header
        expected_events = expected.TimeSeries.series.event

        assert found_header.timeStep._attributes["unit"] == expected_header.timeStep._attributes["unit"]
        assert len(found_events) == len(expected_events)
        assert found_events[0]._attributes["date"] == expected_events[0]._attributes["date"]
        assert found_events[-1]._attributes["date"] == expected_events[-1]._attributes["date"]


def test_sa_multi_timeseries_2_ok_csv_download(fixture_api_sa_with_download_dir):
    """OutputChoices.csv_file_in_download_dir."""
    api = fixture_api_sa_with_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti2

    all_file_paths = api.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        output_choice=OutputChoices.csv_file_in_download_dir,
    )
    assert len(all_file_paths) == 2
    assert all_file_paths[0].name == "gettimeseriesmulti_kw215712_ddy_20050101t000000z_20050102t000000z.csv"
    assert all_file_paths[1].name == "gettimeseriesmulti_kw322613_qby_20050101t000000z_20050102t000000z.csv"

    mapper_csv_expected = request_data.get_expected_dfs_from_csvs()
    for downloaded_file in all_file_paths:
        df_found = pd.read_csv(filepath_or_buffer=downloaded_file, sep=",")
        df_expected = mapper_csv_expected[downloaded_file.stem]
        pd.testing.assert_frame_equal(left=df_found, right=df_expected)
