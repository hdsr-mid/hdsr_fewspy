from dataclasses import dataclass
from fewspy.constants.choices import PiRestDocumentFormatChoices
from fewspy.constants.choices import TimeZoneChoices

import logging
import typing
import validators


logger = logging.getLogger(__name__)


@dataclass
class PiSettings:
    """
    Usage example:
        pi_settings_production = PiSettings(
            settings_name='whatever you want',
            document_version="1.25",
            document_format=PiRestDocumentFormatChoices.json.value,
            ssl_verify=True,
            domain="webwis-prd01.ad.hdsr.nl",
            port=8081,
            service="OwdPiService",
            filter_id="owdapi-opvlwater-noneq",
            module_instance_id="WerkFilter",
            time_zone=TimeZoneChoices.gmt_0.value,
        )
    """

    settings_name: str
    #
    domain: str
    port: int
    service: str
    #
    document_version: float
    document_format: str
    filter_id: str
    module_instance_id: str
    time_zone: str  # see TimeZoneChoices
    #
    ssl_verify: bool

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

    def __post_init__(self) -> None:
        """Validate dtypes and ensure that str objects not being empty."""
        for field_name, field_def in self.__dataclass_fields__.items():
            if isinstance(field_def.type, typing._SpecialForm):
                # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                continue
            try:
                expected_dtype = field_def.type.__origin__
            except AttributeError:
                # In case of non-typing types (such as <class 'int'>, for instance)
                expected_dtype = field_def.type
            if isinstance(expected_dtype, typing._SpecialForm):
                # case of typing.Union[…] or typing.ClassVar[…]
                expected_dtype = field_def.type.__args__

            actual_value = getattr(self, field_name)
            assert isinstance(actual_value, expected_dtype), (
                f"PiSettings '{field_name}={actual_value}' must be of type '{expected_dtype}' and "
                f"not '{type(actual_value)}'"
            )
            if isinstance(actual_value, str):
                assert actual_value, f"PiSettings '{field_name}={actual_value}' must cannot be an empty string"

        if not validators.url(value=self.base_url) == True:  # noqa
            raise AssertionError(f"base_url '{self.base_url}' must be valid")
        if not validators.url(value=self.test_url) == True:  # noqa
            raise AssertionError(f"test_url '{self.test_url}' must be valid")


pi_settings_mocked = PiSettings(
    settings_name="mocked",
    document_version=1.25,
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    domain="localhost",
    port=9999,
    service="mocked",
    filter_id="mocked",
    module_instance_id="mocked",
    time_zone=TimeZoneChoices.gmt_0.value,
)

pi_settings_sa = PiSettings(
    settings_name="default stand-alone",
    document_version=1.25,
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    domain="localhost",
    port=8080,
    service="FewsWebServices",
    filter_id="INTERAL-API",
    module_instance_id="ImportOpvlWater",
    time_zone=TimeZoneChoices.gmt_0.value,
)

pi_settings_production = PiSettings(
    settings_name="default production",
    document_version=1.25,
    document_format=PiRestDocumentFormatChoices.json.value,
    ssl_verify=True,
    domain="webwis-prd01.ad.hdsr.nl",
    port=8081,
    service="OwdPiService",
    filter_id="owdapi-opvlwater-noneq",
    module_instance_id="WerkFilter",
    time_zone=TimeZoneChoices.gmt_0.value,
)
