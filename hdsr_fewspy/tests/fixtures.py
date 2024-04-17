from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def fixture_api_efcis_prod_point_biologie_no_download_dir():
    api = Api(pi_settings=DefaultPiSettingsChoices.efcis_production_point_biologie)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "efcis_production_point_biologie"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "DataSciencePiService"
    assert api.pi_settings.module_instance_ids == "Import_IMmetingen_Biologie"
    assert api.pi_settings.document_version == 1.25
    assert not api.request_settings.updated_request_period
    return api


@pytest.fixture(scope="function")
def fixture_api_wis_sa_work_no_download_dir():
    api = Api(pi_settings=DefaultPiSettingsChoices.wis_stand_alone_point_work)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "wis_stand_alone_point_work"
    assert api.pi_settings.domain == "localhost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    assert not api.request_settings.updated_request_period
    return api


@pytest.fixture(scope="function")
def fixture_api_wis_sa_raw_no_download_dir():
    api = Api(pi_settings=DefaultPiSettingsChoices.wis_stand_alone_point_raw)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "wis_stand_alone_point_raw"
    assert api.pi_settings.domain == "localhost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "ImportOpvlWater"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    assert not api.request_settings.updated_request_period
    return api


@pytest.fixture(scope="function")
def fixture_api_wis_sa_validated_no_download_dir():
    api = Api(pi_settings=DefaultPiSettingsChoices.wis_stand_alone_point_validated)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "wis_stand_alone_point_validated"
    assert api.pi_settings.domain == "localhost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "MetingenFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    assert not api.request_settings.updated_request_period
    return api


@pytest.fixture(scope="function")
def fixture_api_wis_sa_work_with_download_dir(tmpdir_factory):
    output_dir = tmpdir_factory.mktemp("hdsr_fewspy_test_dir")  # tmpdir_factory can do session scope. nice!
    output_dir_path = Path(output_dir)
    assert output_dir_path.is_dir()
    api = Api(pi_settings=DefaultPiSettingsChoices.wis_stand_alone_point_work, output_directory_root=output_dir_path)
    assert isinstance(api.output_dir, Path)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "wis_stand_alone_point_work"
    assert api.pi_settings.domain == "localhost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    assert not api.request_settings.updated_request_period
    return api
