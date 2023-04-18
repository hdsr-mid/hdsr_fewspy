from fewspy.api import Api
from fewspy.constants.choices import OutputChoices
from fewspy.constants.pi_settings import pi_settings_production
from fewspy.constants.pi_settings import pi_settings_sa
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixture_api_sa_json_memory():
    api = Api(pi_settings=pi_settings_sa, default_output_choice=OutputChoices.json_response_in_memory)
    assert api.pi_settings.base_url == pi_settings_sa.base_url
    assert api.pi_settings.document_format == "PI_JSON"
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "default stand-alone"
    assert api.pi_settings.filter_ids == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    return api


@pytest.fixture(scope="session")
def fixture_api_sa_json_download(tmpdir_factory):
    output_dir = tmpdir_factory.mktemp("hdsr_fewspy_test_dir")  # tmpdir_factory can do session scope. nice!
    output_dir_path = Path(output_dir)
    assert output_dir_path.is_dir()
    api = Api(
        pi_settings=pi_settings_sa,
        default_output_choice=OutputChoices.json_file_in_download_dir,
        output_directory_root=output_dir_path,
    )
    assert api.pi_settings.base_url == pi_settings_sa.base_url
    assert api.pi_settings.document_format == "PI_JSON"
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "default stand-alone"
    assert api.pi_settings.filter_ids == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    return api


@pytest.fixture(scope="session")
def fixture_api_production():
    api = Api(pi_settings=pi_settings_production)
    return api
