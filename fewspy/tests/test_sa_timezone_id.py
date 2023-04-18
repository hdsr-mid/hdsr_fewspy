from fewspy.constants.choices import OutputChoices
from fewspy.constants.choices import TimeZoneChoices
from fewspy.tests.fixtures import fixture_api_sa_json_memory


# silence flake8
fixture_api_sa_json_memory = fixture_api_sa_json_memory


def test_sa_timezone_response(fixture_api_sa_json_memory):
    assert fixture_api_sa_json_memory.output_choice == OutputChoices.json_response_in_memory

    responses = fixture_api_sa_json_memory.get_timezone_id()
    assert len(responses) == 1
    response = responses[0]
    assert response.text == TimeZoneChoices.gmt.value
