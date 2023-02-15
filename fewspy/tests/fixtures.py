from fewspy.constants import API_BASE_URL_TEST
from fewspy.daniel.src.fewspy.api import Api

import pytest
import responses


@pytest.fixture(scope="session")
@responses.activate
def api_fixture():
    """Avoid mocking 2 responses in every test as instantiating Api does an additional GET request to validation_url."""
    # mock base_url
    base_url = API_BASE_URL_TEST
    responses.add(method=responses.GET, url=base_url, status=200)

    api = Api(base_url=API_BASE_URL_TEST)
    return api
