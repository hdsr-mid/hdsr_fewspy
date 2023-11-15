from dataclasses import asdict
from dataclasses import dataclass
from hdsr_fewspy.constants import github
from hdsr_pygithub import GithubFileDownloader
from typing import Dict

import logging
import pandas as pd
import typing


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
    time_zone: float
    #
    ssl_verify: bool
    document_format: str = None  # updated based on api.output_choice during Api instance

    def __repr__(self) -> str:
        return f"{self.all_fields}"

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
        - http://localhost:8081/FewsWebServices/test/fewspiservicerest/test.html
        - http://webwis-prd01.ad.hdsr.nl:8081/OwdPiService/test/fewspiservicerest/test.html
        """
        return f"http://{self.domain}:{self.port}/{self.service}/test/fewspiservicerest/test.html"

    def __post_init__(self) -> None:
        """Validate dtypes and ensure that str objects not being empty."""
        for field_name, field_def in self.__dataclass_fields__.items():  # noqa
            if isinstance(field_def.type, typing._SpecialForm):  # noqa
                # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                continue
            try:
                expected_dtype = field_def.type.__origin__
            except AttributeError:
                # In case of non-typing types (such as <class 'int'>, for instance)
                expected_dtype = field_def.type
            if isinstance(expected_dtype, typing._SpecialForm):  # noqa
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

    @property
    def all_fields(self) -> Dict:
        return asdict(self)


class GithubPiSettingDefaults:
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

    def __init__(self, github_personal_access_token: str):
        self.github_personal_access_token = github_personal_access_token
        self._df_github_settings = None

    @property
    def df_github_settings(self) -> pd.DataFrame:
        if self._df_github_settings is not None:
            return self._df_github_settings
        github_downloader = GithubFileDownloader(
            target_file=github.GITHUB_HDSR_FEWSPY_AUTH_SETTINGS_TARGET_FILE,
            allowed_period_no_updates=github.GITHUB_HDSR_FEWSPY_AUTH_ALLOWED_PERIOD_NO_UPDATES,
            repo_name=github.GITHUB_HDSR_FEWSPY_AUTH_REPO_NAME,
            branch_name=github.GITHUB_HDSR_FEWSPY_AUTH_BRANCH_NAME,
            repo_organisation=github.GITHUB_ORGANISATION,
            personal_access_token=self.github_personal_access_token,
        )
        df = pd.read_csv(filepath_or_buffer=github_downloader.get_download_url(), sep=";")
        assert sorted(df.columns) == sorted(self.expected_columns), "code_error"
        self._df_github_settings = df
        return self._df_github_settings

    def _read_github(self, settings_name: str) -> pd.Series:
        logger.info(f"get_on_the_fly_pi_settings for setttings_name '{settings_name}'")
        df_slice = self.df_github_settings[self.df_github_settings["settings_name"] == settings_name]
        if df_slice.empty:
            available_setting_names = self.df_github_settings["settings_name"].tolist()
            msg = f"pi settings_name '{settings_name}' is not in available setting_names '{available_setting_names}'"
            raise AssertionError(msg)
        assert len(df_slice) == 1, "code error _read_github"
        pd_series = df_slice.iloc[0]
        return pd_series

    def get_pi_settings(self, settings_name: str) -> PiSettings:
        pd_series = self._read_github(settings_name=settings_name)
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
