from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.pi_settings import github_pi_setting_defaults
from hdsr_fewspy.exceptions import UserNotFoundInHdsrFewspyAuthError

import pytest


def test_custom_secrets():
    pi_settings_sa = github_pi_setting_defaults.get_pi_settings(settings_name="standalone")

    # valid email as arg (not from secrets.env), and token from secrets.env
    api = Api(github_email="renier.kramer@hdsr.nl", pi_settings=pi_settings_sa)
    assert api.pi_settings.ssl_verify == True  # noqa
    assert api.pi_settings.settings_name == "standalone"
    assert api.pi_settings.domain == "localhost"
    assert api.pi_settings.filter_id == "INTERNAL-API"
    assert api.pi_settings.service == "FewsWebServices"
    assert api.pi_settings.module_instance_ids == "WerkFilter"
    assert api.pi_settings.document_version == 1.25
    assert api.pi_settings.port == 8080
    assert not api.request_settings.updated_request_period

    # invalid email as arg (not from secrets.env), and token from secrets.env
    try:
        Api(github_email="aa", pi_settings=pi_settings_sa)
    except Exception as err:
        assert err.args[0] == "email 'aa' must be str of at least 5 chars"

    # invalid email as arg (not from secrets.env), and token from secrets.env
    try:
        Api(github_email="invalid_email@", pi_settings=pi_settings_sa)
    except Exception as err:
        assert err.args[0] == "email 'invalid_email@' is invalid"

    # valid unregistered email as arg (not from secrets.env), and token from secrets.env
    with pytest.raises(UserNotFoundInHdsrFewspyAuthError) as err:
        Api(github_email="unregistered@gmail.com", pi_settings=pi_settings_sa)
    assert err.value.args[0] == "github_email unregistered@gmail.com is registered 0 times in hdsr_fewspy_auth"
