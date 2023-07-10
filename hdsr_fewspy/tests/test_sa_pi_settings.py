from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.pi_settings import PiSettings
from hdsr_fewspy.tests.fixtures import fixture_api_sa_work_no_download_dir


# silence flake8
fixture_api_sa_work_no_download_dir = fixture_api_sa_work_no_download_dir


def test_pi_settings(fixture_api_sa_work_no_download_dir):
    settings_obj = fixture_api_sa_work_no_download_dir.pi_settings
    assert isinstance(settings_obj, PiSettings)
    assert isinstance(settings_obj.all_fields, dict)
    found_str = str(settings_obj.all_fields)
    expected_str = (
        "{'settings_name': 'wis_stand_alone_point_work', 'domain': 'localhost', 'port': 8080, 'service': "
        "'FewsWebServices', 'document_version': 1.25, 'filter_id': 'INTERNAL-API', 'module_instance_ids': "
        "'WerkFilter', 'time_zone': 0.0, 'ssl_verify': True, 'document_format': "
        "<PiRestDocumentFormatChoices.json: 'PI_JSON'>}"
    )
    assert found_str == expected_str


def test_custom_pi_settings():
    custom_settings = PiSettings(
        settings_name="does not matter blabla",
        document_version=1.25,
        ssl_verify=True,
        domain="localhost",
        port=8080,
        service="FewsWebServices",
        filter_id="INTERNAL-API",
        module_instance_ids="WerkFilter",
        time_zone=TimeZoneChoices.eu_amsterdam.value,
    )
    api = Api(pi_settings=custom_settings)
    assert api.pi_settings.time_zone == 1.0 == TimeZoneChoices.eu_amsterdam.value
