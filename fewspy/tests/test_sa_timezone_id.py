from fewspy.constants.choices import OutputChoices
from fewspy.constants.choices import TimeZoneChoices
from fewspy.tests.fixtures import fixture_api_sa_no_download_dir


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_no_download_dir


def test_sa_timezone_response(fixture_api_sa_no_download_dir):
    responses = fixture_api_sa_no_download_dir.get_timezone(output_choice=OutputChoices.json_response_in_memory)
    assert len(responses) == 1
    response = responses[0]
    assert response.text == TimeZoneChoices.gmt
