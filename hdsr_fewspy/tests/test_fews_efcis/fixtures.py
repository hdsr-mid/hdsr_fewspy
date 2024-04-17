from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices

import pytest


@pytest.fixture(scope="function")
def fixture_api_efcis_production_point_fc_no_download_dir():
    api = Api(pi_settings=DefaultPiSettingsChoices.efcis_production_point_fc)
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