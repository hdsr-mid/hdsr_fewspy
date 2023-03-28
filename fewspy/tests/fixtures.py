from fewspy.api import Api
from fewspy.constants.pi_settings import pi_settings_mocked
from fewspy.constants.pi_settings import pi_settings_production
from fewspy.constants.pi_settings import pi_settings_sa

import pytest
import responses


@pytest.fixture(scope="session")
@responses.activate
def api_mocked_fixture():
    """Avoid mocking 2 responses in every test as instantiating Api does an additional GET request to validation_url."""
    responses.add(method=responses.GET, url=pi_settings_mocked.base_url, status=200)  # mock base_url
    api = Api(pi_settings=pi_settings_mocked)
    return api


@pytest.fixture(scope="session")
@responses.activate
def api_sa_fixture():
    """Avoid mocking 2 responses in every test as instantiating Api does an additional GET request to validation_url."""
    responses.add(method=responses.GET, url=pi_settings_sa.base_url, status=200)  # mock base_url
    api = Api(pi_settings=pi_settings_sa)
    return api


@pytest.fixture(scope="session")
@responses.activate
def api_production_fixture():
    """Avoid mocking 2 responses in every test as instantiating Api does an additional GET request to validation_url."""
    responses.add(method=responses.GET, url=pi_settings_production.base_url, status=200)  # mock base_url
    api = Api(pi_settings=pi_settings_production)
    return api
