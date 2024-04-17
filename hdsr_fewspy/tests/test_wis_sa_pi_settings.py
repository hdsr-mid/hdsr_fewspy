from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.pi_settings import GithubPiSettingDefaults
from hdsr_fewspy.constants.pi_settings import PiSettings
from hdsr_fewspy.tests.fixtures import fixture_api_wis_sa_work_no_download_dir


# silence flake8
fixture_api_wis_sa_work_no_download_dir = fixture_api_wis_sa_work_no_download_dir


def test_wis_sa_pi_settings(fixture_api_wis_sa_work_no_download_dir):
    settings_obj = fixture_api_wis_sa_work_no_download_dir.pi_settings
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


def test_wis_sa_custom_pi_settings():
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


def test_wis_sa_default_settings_match_with_auth_repo(fixture_api_wis_sa_work_no_download_dir):
    api = fixture_api_wis_sa_work_no_download_dir
    github_pi_setting_defaults = GithubPiSettingDefaults(api.secrets.github_personal_access_token)
    settings_online_in_auth_repo = set(github_pi_setting_defaults.df_github_settings["settings_name"].to_list())
    local_setting_in_this_repo = set([x.value for x in DefaultPiSettingsChoices.get_all()])

    local_but_not_online = local_setting_in_this_repo.difference(settings_online_in_auth_repo)
    online_but_not_local = settings_online_in_auth_repo.difference(local_setting_in_this_repo)

    assert not local_but_not_online, f"local_but_not_online {local_but_not_online}"
    assert not online_but_not_local, f"online_but_not_local {online_but_not_local}"
