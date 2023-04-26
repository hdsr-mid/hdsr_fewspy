from dataclasses import asdict
from dataclasses import dataclass
from hdsr_fewspy.constants import github
from hdsr_pygithub import GithubFileDownloader
from typing import Dict

import logging
import pandas as pd
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
            ssl_verify=True,
            domain="webwis-prd01.ad.hdsr.nl",
            port=8081,
            service="OwdPiService",
            filter_id="owdapi-opvlwater-noneq",
            module_instance_ids="WerkFilter",
            time_zone=TimeZoneChoices.gmt_0.value,
        )

    Note that document_format (JSON/XMl) is automatically set (based on api.output_choice) during Api instance
    """

    settings_name: str
    #
    domain: str
    port: int
    service: str
    #
    document_version: float
    filter_id: str
    module_instance_ids: str
    time_zone: float  # see constants.choices.TimeZoneChoices
    #
    ssl_verify: bool
    document_format: str = None  # updated based on api.output_choice during Api instance

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

            if field_name == "document_format":
                continue
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

    @property
    def all_fields(self) -> Dict:
        return asdict(self)


class GithubPiSettings:

    expected_columns = [
        "settings_name",
        "document_version",
        "ssl_verify",
        "domain",
        "port",
        "service",
        "filter_id",
        "module_instance_ids",
        "time_zone",
    ]

    @classmethod
    def _read_github(cls, settings_name: str) -> pd.Series:
        logger.info(f"get_on_the_fly_pi_settings for setttings_name {settings_name}")
        github_downloader = GithubFileDownloader(
            target_file=github.GITHUB_HDSR_FEWSPY_AUTH_SETTINGS_TARGET_FILE,
            allowed_period_no_updates=github.GITHUB_HDSR_FEWSPY_AUTH_ALLOWED_PERIOD_NO_UPDATES,
            repo_name=github.GITHUB_HDSR_FEWSPY_AUTH_REPO_NAME,
            branch_name=github.GITHUB_HDSR_FEWSPY_AUTH_BRANCH_NAME,
            repo_organisation=github.GITHUB_ORGANISATION,
        )
        df = pd.read_csv(filepath_or_buffer=github_downloader.get_download_url(), sep=";")
        df_slice = df[df["settings_name"] == settings_name]
        if df_slice.empty:
            available_setting_names = df["settings_name"].tolist()
            msg = f"pi settings_name {settings_name} is not in available setting_names {available_setting_names}"
            raise AssertionError(msg)
        assert len(df_slice) == 1, "code error"
        assert sorted(df.columns) == sorted(cls.expected_columns), "code_error"
        pd_series = df_slice.iloc[0]
        return pd_series

    @classmethod
    def get_pi_settings(cls, settings_name: str) -> PiSettings:
        pd_series = cls._read_github(settings_name=settings_name)
        pi_settings = PiSettings(
            settings_name=pd_series["settings_name"],
            document_version=pd_series["document_version"],
            ssl_verify=bool(pd_series["ssl_verify"]),
            domain=pd_series["domain"],
            port=int(pd_series["port"]),
            service=pd_series["service"],
            filter_id=pd_series["filter_id"],
            module_instance_ids=pd_series["module_instance_ids"],
            time_zone=float(pd_series["time_zone"]),
        )
        return pi_settings


pi_settings_sa = GithubPiSettings.get_pi_settings(settings_name="standalone")
pi_settings_production = GithubPiSettings.get_pi_settings(settings_name="production")
