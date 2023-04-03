from fewspy.constants.pi_settings import pi_settings_mocked
from fewspy.tests.fixtures import api_mocked_fixture


# silence flake8
api_mocked_fixture = api_mocked_fixture


def test_api(api_mocked_fixture):
    assert api_mocked_fixture.pi_settings.base_url == pi_settings_mocked.base_url
    assert api_mocked_fixture.pi_settings.document_format == "PI_JSON"
    assert api_mocked_fixture.pi_settings.ssl_verify == True  # noqa
