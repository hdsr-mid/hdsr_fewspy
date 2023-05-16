from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices


def test_wrong_token():
    non_existing_token = "ADSFADZFBDHweffSDFASDGdsv234fsdSDF@#$ds"
    try:
        Api(github_personal_access_token=non_existing_token, pi_settings=DefaultPiSettingsChoices.wis_stand_alone)
    except Exception as err:
        assert err.args[0] == f"invalid personal_access_token {non_existing_token} as we cannot get user_html_url"
