from datetime import datetime
from hdsr_fewspy import api_calls
from hdsr_fewspy import exceptions
from hdsr_fewspy.constants.choices import DefaultPiSettingsChoices
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.constants.paths import SECRETS_ENV_PATH
from hdsr_fewspy.constants.pi_settings import GithubPiSettingDefaults
from hdsr_fewspy.constants.pi_settings import PiSettings
from hdsr_fewspy.constants.request_settings import get_default_request_settings
from hdsr_fewspy.constants.request_settings import RequestSettings
from hdsr_fewspy.permissions import Permissions
from hdsr_fewspy.retry_session import RetryBackoffSession
from hdsr_fewspy.secrets import Secrets
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import geopandas as gpd
import logging
import os
import pandas as pd
import urllib3  # noqa


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = logging.getLogger(__name__)


class Api:
    """Python API for the Deltares FEWS PI REST Web Service.

    The methods corresponding with the FEWS PI-REST requests. For more info on how to work with the FEWS REST Web
    Service, visit the Deltares website: https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service.
    """

    def __init__(
        self,
        github_personal_access_token: str = None,
        secrets_env_path: Union[str, Path] = SECRETS_ENV_PATH,
        pi_settings: Union[PiSettings, DefaultPiSettingsChoices] = None,
        output_directory_root: Union[str, Path] = None,
    ):
        self.secrets = Secrets(
            github_personal_access_token=github_personal_access_token,
            secrets_env_path=secrets_env_path,
        )
        self.permissions = Permissions(secrets=self.secrets)
        self.output_dir = self.__get_output_dir(output_directory_root=output_directory_root)
        self.pi_settings = self.__validate_pi_settings(pi_settings=pi_settings)
        self.request_settings: RequestSettings = get_default_request_settings()
        self.retry_backoff_session = RetryBackoffSession(
            _request_settings=self.request_settings,
            pi_settings=self.pi_settings,
            output_dir=self.output_dir,
        )
        self.__ensure_service_is_running()

    @staticmethod
    def __get_output_dir(output_directory_root: Union[str, Path] = None) -> Optional[Path]:
        if output_directory_root is None:
            return None
        # check 1
        output_directory_root = Path(output_directory_root)
        assert output_directory_root.is_dir(), f"output_directory_root {output_directory_root} must exist"
        # check 2
        is_dir_writable = os.access(path=output_directory_root.as_posix(), mode=os.W_OK)
        assert is_dir_writable, f"output_directory_root {output_directory_root} must be writable"
        # create subdir
        output_dir = output_directory_root / f"hdsr_fewspy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return output_dir

    def __log_not_running_service(self, err: Exception = None, response: ResponseType = None) -> None:
        error = f"{response.text}, {err}" if response else str(err)
        msg = (
            f"Piwebservice is not running, Ensure that you can visit the test page '{self.pi_settings.test_url}', "
            f"err={error}"
        )
        if self.pi_settings.domain == "localhost":
            msg += ". Please make sure FEWS SA webservice is running and start embedded tomcat server via F12 key."
            raise exceptions.StandAloneFewsWebServiceNotRunningError(msg)
        raise exceptions.FewsWebServiceNotRunningError(msg)

    def __ensure_service_is_running(self) -> None:
        """Just request endpoint with smallest response (=timezonid)."""
        try:
            response = self.get_timezone_id(output_choice=OutputChoices.json_response_in_memory)
            if response.ok:
                logger.info(f"PiWebService is running (see test page: '{self.pi_settings.test_url}')")
                return
            self.__log_not_running_service(err=None, response=response)
        except Exception as err:
            self.__log_not_running_service(err=err, response=None)

    def __validate_pi_settings(self, pi_settings: Union[PiSettings, DefaultPiSettingsChoices] = None) -> PiSettings:
        github_pi_setting_defaults = GithubPiSettingDefaults(self.secrets.github_personal_access_token)

        if pi_settings is None:
            pi_settings = github_pi_setting_defaults.get_pi_settings(
                DefaultPiSettingsChoices.wis_production_point_validated.value
            )
            logger.info(f"no pi_settings defined, so using '{pi_settings.settings_name}'")
        elif isinstance(pi_settings, DefaultPiSettingsChoices):
            pi_settings = github_pi_setting_defaults.get_pi_settings(settings_name=pi_settings.value)
            logger.info(f"default pi_settings defined '{pi_settings.settings_name}'")
        elif isinstance(pi_settings, PiSettings):
            logger.info(f"custom pi_settings defined '{pi_settings.settings_name}'")
            mapper = {
                # setting: (used, allowed)
                "domain": (pi_settings.domain, self.permissions.allowed_domain),
                "module_instance_id": (pi_settings.module_instance_ids, self.permissions.allowed_module_instance_id),
                "timezone": (pi_settings.time_zone, TimeZoneChoices.get_all_values()),
                "filter_id": (pi_settings.filter_id, self.permissions.allowed_filter_id),
                "service": (pi_settings.service, self.permissions.allowed_service),
            }
            for setting, value in mapper.items():
                used_value, allowed_values = value
                assert isinstance(
                    allowed_values, list
                ), f"code error __validate_pi_settings: allowed_values {allowed_values} must be a list"
                if used_value in allowed_values:
                    continue
                msg = f"setting='{setting}' used_value='{used_value}' is not in allowed_values='{allowed_values}'"
                raise exceptions.PiSettingsError(msg)
        else:
            default_options = DefaultPiSettingsChoices.get_all()
            msg = (
                f"pi_settings {pi_settings} must be a either None, or a str (choose from '{default_options}'), or a "
                f"custom PiSettings (see README.ml example how to create one)"
            )
            raise NotImplementedError(msg)
        return pi_settings

    def get_parameters(self, output_choice: OutputChoices) -> Union[ResponseType, pd.DataFrame]:
        # show_attributes does not make a difference in response (both for Pi_JSON and PI_XML)
        api_call = api_calls.GetParameters(
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    def get_filters(self, output_choice: OutputChoices) -> ResponseType:
        api_call = api_calls.GetFilters(output_choice=output_choice, retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    def get_locations(
        self, output_choice: OutputChoices, show_attributes: bool = True
    ) -> Union[ResponseType, gpd.GeoDataFrame]:
        api_call = api_calls.GetLocations(
            show_attributes=show_attributes,
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    def get_qualifiers(self, output_choice: OutputChoices) -> pd.DataFrame:
        api_call = api_calls.GetQualifiers(
            output_choice=output_choice, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    def get_timezone_id(self, output_choice: OutputChoices) -> ResponseType:
        """Get FEWS timezone_id the FEWS API is running on."""
        api_call = api_calls.GetTimeZoneId(
            output_choice=output_choice, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    def get_samples(
        self, output_choice: OutputChoices, start_time: datetime, end_time: datetime
    ) -> Union[ResponseType, pd.DataFrame]:
        api_call = api_calls.GetSamples(
            start_time=start_time,
            end_time=end_time,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    def get_time_series_statistics(
        self,
        output_choice: OutputChoices,
        #
        start_time: datetime,
        end_time: datetime,
        location_id: str,
        parameter_id: str,
        qualifier_id: str = None,
        thinning: int = None,
        omit_empty_time_series: bool = True,
    ) -> ResponseType:
        """
        Example response PI_JSON = {
            "timeSeries": [
                {
                    "header": {
                        "endDate": {"date": "2012-01-02", "time": "00:00:00"},
                        "firstValueTime": {"date": "2012-01-01", "time": "00:15:00"},
                        "lastValueTime": {"date": "2012-01-02", "time": "00:00:00"},
                        "lat": "52.08992726570302",
                        "locationId": "OW433001",
                        "lon": "4.9547458967486095",
                        "maxValue": "-0.28",
                        "minValue": "-0.44",
                        "missVal": "-999.0",
                        "moduleInstanceId": "WerkFilter",
                        "parameterId": "H.G.0",
                        "startDate": {"date": "2012-01-01", "time": "00:00:00"},
                        "stationName": "HAANWIJKERSLUIS_4330-w_Leidsche " "Rijn",
                        "timeStep": {"unit": "nonequidistant"},
                        "type": "instantaneous",
                        "units": "mNAP",
                        "valueCount": "102",
                        "x": "125362.0",
                        "y": "455829.0",
                        "z": "-0.18",
                    }
                }
            ]
        }
        """
        api_call = api_calls.GetTimeSeriesStatistics(
            start_time=start_time,
            end_time=end_time,
            location_ids=location_id,
            parameter_ids=parameter_id,
            qualifier_ids=qualifier_id,
            thinning=thinning,
            omit_empty_time_series=omit_empty_time_series,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    def get_time_series_single(
        self,
        output_choice: OutputChoices,
        #
        start_time: Union[datetime, str],
        end_time: Union[datetime, str],
        location_id: str,
        parameter_id: str,
        qualifier_id: str = None,
        thinning: int = None,
        omit_empty_time_series: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ) -> Union[List[ResponseType], pd.DataFrame]:
        """Single means: use max 1 location_id and/or parameter_id and/or qualifier_id.

        One large call can result in multiple small calls and therefore multiple responses. If your output_choice is
        json/xml in memory, then you get a list with >=1 responses and arguments 'flag_threshold' and
        'drop_missing_values' have no effect.
        For more info on flags see: https://publicwiki.deltares.nl/display/FEWSDOC/D+Time+Series+Flag.

        start_time and end_time can be of type:
            - datetime: a python datetime.datetime
            - str: a string with format "%Y-%m-%dT%H:%M:%SZ" e.g. "2012-01-01T00:00:00Z
        """
        api_call = api_calls.GetTimeSeriesSingle(
            start_time=start_time,
            end_time=end_time,
            location_ids=location_id,
            parameter_ids=parameter_id,
            qualifier_ids=qualifier_id,
            thinning=thinning,
            omit_empty_time_series=omit_empty_time_series,
            drop_missing_values=drop_missing_values,
            flag_threshold=flag_threshold,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    def get_time_series_multi(
        self,
        output_choice: OutputChoices,
        #
        start_time: Union[datetime, str],
        end_time: Union[datetime, str],
        location_ids: List[str] = None,
        parameter_ids: List[str] = None,
        qualifier_ids: List[str] = None,
        thinning: int = None,
        omit_empty_time_series: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ) -> List[Path]:
        """Multi means: use >=1 location_id and/or parameter_id and/or qualifier_id.

        The api call below results in 4 unique location_parameter_qualifier combinations: OW433001_hg0, OW433001_hgd,
        OW433002_hg0, OW433002_hgd. Per unique combination we do >=1 requests which therefore result in >=1 responses.
        If output_choice is xml/json to file, then each response results in a file and arguments 'flag_threshold' and
        'drop_missing_values' have no effect.
        For more info on flags see: https://publicwiki.deltares.nl/display/FEWSDOC/D+Time+Series+Flag.

        start_time and end_time can be of type:
            - datetime: a python datetime.datetime
            - str: a string with format "%Y-%m-%dT%H:%M:%SZ" e.g. "2012-01-01T00:00:00Z
        """
        api_call = api_calls.GetTimeSeriesMulti(
            start_time=start_time,
            end_time=end_time,
            location_ids=location_ids,
            parameter_ids=parameter_ids,
            qualifier_ids=qualifier_ids,
            thinning=thinning,
            omit_empty_time_series=omit_empty_time_series,
            drop_missing_values=drop_missing_values,
            flag_threshold=flag_threshold,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        all_file_paths = api_call.run()
        return all_file_paths


# TODO: add __repr__ to pi_settings so that users in R can easily sea what pi_settings they are using

# TODO: add url Deltares with flag info

# TODO: don't use strings as urls...

# TODO: Ciska wel interesse wel in:
#  --------------------------------
#  get_samples (grote request)
#  - Deltares is hier begin 2024 klaar. Nu geeft FEWS EFICS piwebservice na 2 of 5 minuten een timeout
#  get_timeseries (grote request)
#  - altijd start + end
#  - altijd omitEmptyTimeSeries op True anders geeft ie minimaal weken aan tijdseries terug
#  - vaak filter_id
#  - soms parameter_id, location_id, moduleinstance_id
#  - heel soms qualifier_id
#  get_parameters (middlegrote request = 400 parameters)
#  get_locations (kleine request = 300 locaties)

# TODO: Ciska geen interesse in: get_qualifiers

# TODO: check of properties goed meekomen in get_timeseries in PI_JSON (in PI_XML gaat het goed) -> Ciska:" bij
#  EFICS werkt niet helemaal lekker. bij get_samples gaat het helemaal fout"

# TODO: van potentieel grote naar kleine request belasting: get_samples, get_timeseries,
#  get_qualifiers (25 groepen * 100k regels per groep), get_parameters (4000), get_locations (300)

# TODO: use onlyHeader=True kan voor get_timeseries en get_samples (beide hebben ook start + eind).
#  Echter, get_qualifiers heeft dat niet. FEWS-WIS response is snel (<1sec). FEWS-EFICS duurt lang (8 sec)
#  get_lcoations duurt 7 sec. Voorstel Ciska: alleen func get_timeseries + get_samples via PiWebService. De andere
#  request disabelen: logger.info('Stuur ciska.overbeek@hdsr.nl een mailtje of dat lijstje mag, dan krijg je er ook
#  nog meer info bij) die lijstjes worden 2 a 3 per jaar script + handmatig ge-update...
