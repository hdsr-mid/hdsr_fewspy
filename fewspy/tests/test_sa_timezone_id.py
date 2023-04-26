from fewspy.constants.choices import OutputChoices
from fewspy.constants.choices import TimeZoneChoices
from fewspy.tests.fixtures import fixture_api_sa_no_download_dir


# silence flake8
fixture_api_sa_no_download_dir = fixture_api_sa_no_download_dir


def test_sa_timezone_response(fixture_api_sa_no_download_dir):
    response = fixture_api_sa_no_download_dir.get_timezone_id(output_choice=OutputChoices.json_response_in_memory)
    assert response.text == "GMT"
    assert TimeZoneChoices.get_tz_float(value=response.text) == TimeZoneChoices.gmt
