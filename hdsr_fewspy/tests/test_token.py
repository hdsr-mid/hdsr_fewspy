from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices
from pathlib import Path


def test_invalid_token():
    non_existing_token = "ADSFADZFBDHweffSDFASDGdsv234fsdSDF@#$ds"
    try:
        Api(
            github_personal_access_token=non_existing_token,
            pi_settings=DefaultPiSettingsChoices.wis_stand_alone_point_raw,
        )
    except Exception as err:
        assert err.args[0] == f"invalid personal_access_token {non_existing_token} as we cannot get user_html_url"


def test_valid_token():
    g_drive = Path("G:")
    secrets_env_path = g_drive / "secrets.env"
    if not secrets_env_path.is_file():
        return

    api = Api(secrets_env_path=secrets_env_path, pi_settings=DefaultPiSettingsChoices.wis_production_point_work)
    assert isinstance(api, Api)
