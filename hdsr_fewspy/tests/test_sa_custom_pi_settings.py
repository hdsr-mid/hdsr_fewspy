from hdsr_fewspy.api import Api
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.pi_settings import PiSettings


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
