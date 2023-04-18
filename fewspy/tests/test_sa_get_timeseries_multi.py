from fewspy.constants.choices import OutputChoices
from fewspy.tests import fixtures_requests
from fewspy.tests.fixtures import fixture_api_sa_json_download
from fewspy.tests.fixtures import fixture_api_sa_json_memory

import json
import pytest


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_json_memory
fixture_api_sa_json_download = fixture_api_sa_json_download


def test_sa_multi_timeseries_wrong_requests(fixture_api_sa_json_memory):
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    # start_time is skipped
    with pytest.raises(TypeError):
        fixture_api_sa_json_memory.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            # start_time: start_time=request_data.start_time
            end_time=request_data.end_time,
        )

    # end_time is skipped
    with pytest.raises(TypeError):  # get_time_series() missing 1 required positional argument: 'end_time'
        fixture_api_sa_json_memory.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.start_time
            # end_time: end_time=request_data.end_time,
        )

    # flipped start_time and end_time
    try:
        fixture_api_sa_json_memory.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.end_time,  # <- flipped start_time with end_time
            end_time=request_data.start_time,  # <- flipped end_time with start_time
        )
    except AssertionError as err:
        err_msg = f"start_time {request_data.end_time} must be earlier than end_time {request_data.start_time}"
        assert err.args[0] == err_msg

    # json_response_in_memory is invalid for multi timeseries request (multi is always download to dir)
    assert fixture_api_sa_json_memory.default_output_choice == OutputChoices.json_response_in_memory
    try:
        fixture_api_sa_json_memory.get_time_series_multi(
            location_ids=request_data.location_ids,
            parameter_ids=request_data.parameter_ids,
            start_time=request_data.start_time,
            end_time=request_data.end_time,
        )
    except Exception as err:
        msg = (
            "invalid output_choice 'json_response_in_memory'. GetTimeSeriesMulti has valid_output_choices "
            "['xml_file_in_download_dir', 'csv_file_in_download_dir', 'json_file_in_download_dir']. See earlier "
            "logging why we use GetTimeSeriesMulti."
        )
        assert err.args[0] == msg


def test_sa_multi_timeseries_ok_requests(fixture_api_sa_json_download):
    assert fixture_api_sa_json_download.default_output_choice == OutputChoices.json_file_in_download_dir
    request_data = fixtures_requests.RequestTimeSeriesMulti1

    all_file_paths = fixture_api_sa_json_download.get_time_series_multi(
        location_ids=request_data.location_ids,
        parameter_ids=request_data.parameter_ids,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )
    assert len(all_file_paths) == 2
    assert all_file_paths[0].name == "timeseries_ow433001_hg0_20120101t000000z_20120102t000000z_0.json"
    assert all_file_paths[1].name == "timeseries_ow433002_hg0_20120101t000000z_20120102t000000z_0.json"

    expected_jsons = request_data.get_expected_jsons()
    for downloaded_file in all_file_paths:
        with open(downloaded_file.as_posix()) as src:
            found_json = json.load(src)
        expected_json = expected_jsons[downloaded_file.stem]
        assert found_json == expected_json