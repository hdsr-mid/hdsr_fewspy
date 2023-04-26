from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.tests.fixtures import fixture_api_sa_no_download_dir

import pytest


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir


def test_sa_filters_json(fixture_api_sa_no_download_dir):
    response = fixture_api_sa_no_download_dir.get_filters(output_choice=OutputChoices.json_response_in_memory)
    assert response.status_code == 200


def test_sa_filters_dataframe(fixture_api_sa_no_download_dir):
    # dataframe is not an allowed output_choice
    with pytest.raises(AssertionError):
        fixture_api_sa_no_download_dir.get_filters(output_choice=OutputChoices.pandas_dataframe_in_memory)
