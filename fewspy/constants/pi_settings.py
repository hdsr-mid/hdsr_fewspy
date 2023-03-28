from dataclasses import dataclass
from fewspy.constants.lala import PiRestDocumentFormatChoices
from fewspy.constants.lala import TimeZoneChoices
from typing import List


@dataclass
class PiSettings:

    document_version: str
    document_format: str
    protocol: str  # SOAP protocol is deprecated! So you can only use REST
    missing_value: float
    allowed_flags: List[int]
    domain: str
    port: int
    service: str
    filter_id: str
    module_instance_id: str
    ssl_verify: bool
    time_zone: str

    @property
    def base_url(self) -> str:
        """For example:
        - http://localhost:8081/FewsWebServices/rest/fewspiservice/v1/
        - http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/rest/fewspiservice/v1/
        """
        return f"http://{self.domain}:{self.port}/{self.service}/rest/fewspiservice/v1/"

    @property
    def test_url(self) -> str:
        """For example:
        - http://localhost:8081/FewsWebServices/test/fewspiservicerest/index.jsp
        - http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/test/fewspiservicerest/index.jsp
        """
        return f"http://{self.domain}:{self.port}/{self.service}/test/fewspiservicerest/index.jsp"


pi_settings_mocked = PiSettings(
    document_version="",
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    protocol="",
    missing_value=-999.0,
    allowed_flags=[0, 1, 2, 3, 4, 5],
    domain="xx",
    port=9999,
    service="",
    filter_id="",
    module_instance_id="",
    time_zone=TimeZoneChoices.gmt_0.value,
)

pi_settings_sa = PiSettings(
    document_version="1.25",
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    protocol="rest",
    missing_value=-999.0,
    allowed_flags=[0, 1, 2, 3, 4, 5],
    domain="localhost",
    port=8081,
    service="FewsWebServices",
    filter_id="INTERAL-API.RUW_OPVL",
    module_instance_id="ImportOpvlWater",
    time_zone=TimeZoneChoices.gmt_0.value,
)

pi_settings_production = PiSettings(
    document_version="1.25",
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    protocol="rest",
    missing_value=-999.0,
    allowed_flags=[0, 1, 2, 3, 4, 5],
    domain="localhost",
    port=8081,
    service="OwdPiService",
    filter_id="owdapi-opvlwater-noneq",
    module_instance_id="WerkFilter",
    time_zone=TimeZoneChoices.gmt_0.value,
)
