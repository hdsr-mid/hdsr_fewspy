from fewspy.constants import API_BASE_URL_TEST
from fewspy.tests.fixtures import api_fixture


# silence flake8
api_fixture = api_fixture


def test_api(api_fixture):
    assert api_fixture.base_url == API_BASE_URL_TEST
    assert api_fixture.document_format == "PI_JSON"
    assert api_fixture.ssl_verify == True  # noqa
