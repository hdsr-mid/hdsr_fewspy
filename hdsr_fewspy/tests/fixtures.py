from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.pi_settings import pi_settings_sa
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixture_api_sa_no_download_dir():
    api = Api(pi_settings=pi_settings_sa)
    assert api.pi_settings.base_url == pi_settings_sa.base_url
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "standalone"
    assert api.pi_settings.domain == "locathost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    return api


@pytest.fixture(scope="session")
def fixture_api_sa_with_download_dir(tmpdir_factory):
    output_dir = tmpdir_factory.mktemp("hdsr_fewspy_test_dir")  # tmpdir_factory can do session scope. nice!
    output_dir_path = Path(output_dir)
    assert output_dir_path.is_dir()
    api = Api(pi_settings=pi_settings_sa, output_directory_root=output_dir_path)
    assert isinstance(api.output_dir, Path)
    assert api.pi_settings.base_url == pi_settings_sa.base_url
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "standalone"
    assert api.pi_settings.domain == "locathost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    return api
