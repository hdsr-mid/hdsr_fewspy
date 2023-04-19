from datetime import datetime
from fewspy import api_calls
from fewspy import exceptions
from fewspy.constants.choices import TimeZoneChoices
from fewspy.constants.paths import HDSR_FEWSPY_VERSION
from fewspy.constants.pi_settings import pi_settings_production
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import default_request_settings
from fewspy.constants.request_settings import RequestSettings
from fewspy.permissions import Permissions
from fewspy.retry_session import RetryBackoffSession
from fewspy.utils.bug_report import create_bug_report_when_error
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import logging
import os
import pandas as pd
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = logging.getLogger(__name__)


class Api:
    """Python API for the Deltares FEWS PI REST Web Service.

    The methods corresponding with the FEWS PI-REST requests. For more info on how to work with the FEWS REST Web
    Service, visit the Deltares website: https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service.
    """

    def __init__(
        self,
        pi_settings: PiSettings = pi_settings_production,
        output_directory_root: Union[str, Path] = None,
    ):
        self.permissions = Permissions()
        self.output_dir = self._get_output_dir(output_directory_root=output_directory_root)
        self.pi_settings = self._validate_pi_settings(pi_settings=pi_settings)
        self.request_settings: RequestSettings = default_request_settings
        self.retry_backoff_session = RetryBackoffSession(
            _request_settings=self.request_settings,
            pi_settings=self.pi_settings,
            output_dir=self.output_dir,
        )
        self._ensure_service_is_running()
        self.hdsr_fewspy_version = HDSR_FEWSPY_VERSION

    @staticmethod
    def _get_output_dir(output_directory_root: Union[str, Path] = None) -> Optional[Path]:
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

    @create_bug_report_when_error
    def _ensure_service_is_running(self) -> None:
        # check endpoint with smallest response (=timezonid)
        response = requests.get(url=f"{self.pi_settings.base_url}timezoneid/", verify=self.pi_settings.ssl_verify)
        if response.ok:
            logger.info("PiWebService is running")
            return
        msg = (
            f"Piwebservice is not running, err={response.text}. Ensure that you can visit the test page "
            f"{self.pi_settings.test_url}"
        )
        if self.pi_settings.domain == "localhost":
            msg += ". Please make sure FEWS SA webservice is running and start embedded tomcat server via F12 key."
            raise exceptions.StandAloneFewsWebServiceNotRunningError(msg)
        raise exceptions.FewsWebServiceNotRunningError(msg)

    def _validate_pi_settings(self, pi_settings: PiSettings) -> PiSettings:
        if not isinstance(pi_settings, PiSettings):
            raise AssertionError("pi_settings must be a PiSettings, see README.ml example how to create one")
        mapper = {
            # setting: (used, allowed)
            "domain": (pi_settings.domain, self.permissions.allowed_domain),
            "module_instance_id": (pi_settings.module_instance_ids, self.permissions.allowed_module_instance_id),
            "timezone": (pi_settings.time_zone, TimeZoneChoices.get_all()),
            "filter_id": (pi_settings.filter_ids, self.permissions.allowed_filter_id),
            "service": (pi_settings.service, self.permissions.allowed_service),
        }
        for setting, value in mapper.items():
            used, allowed = value
            assert isinstance(allowed, list), f"code error, {allowed} must be a list"
            if used in allowed:
                continue
            raise exceptions.PiSettingsError(f"{setting} has {used} which is not in allowed {allowed}")

        return pi_settings

    # @create_bug_report_when_error
    def get_parameters(self, output_choice: str) -> pd.DataFrame:
        """Get FEWS parameters as a pandas DataFrame."""
        api_call = api_calls.GetParameters(
            output_choice=output_choice, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_filters(self, output_choice: str) -> List[Dict]:
        """Get FEWS filters as a list with dictionaries."""
        api_call = api_calls.GetFilters(output_choice=output_choice, retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_locations(self, output_choice: str, show_attributes: bool = True):
        """Get FEWS locations as a geopandas GeoDataFrame.
        Args:
            - show_attributes (bool): If True, then location attributes will be include as columns in the DataFrame.
        Returns:
            gpd (geopandas.GeoDataFrame): GeoDataFrame with index "id" and columns "name" and "group_id".
        """
        api_call = api_calls.GetLocations(
            show_attributes=show_attributes,
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_qualifiers(self, output_choice: str) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame

        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        api_call = api_calls.GetQualifiers(
            output_choice=output_choice, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_timezone(self, output_choice: str) -> List[requests.models.Response]:
        """Get FEWS timezone_id the FEWS API is running on."""
        api_call = api_calls.GetTimeZoneId(
            output_choice=output_choice, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_samples(self, output_choice: str, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Get FEWS samples as a pandas DataFrame."""
        api_call = api_calls.GetSamples(
            start_time=start_time,
            end_time=end_time,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_time_series_single(
        self,
        output_choice: str,
        #
        start_time: datetime,
        end_time: datetime,
        location_id: str,
        parameter_id: str,
        qualifier_id: str = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ) -> Union[List[requests.models.Response], List[pd.DataFrame]]:
        assert start_time < end_time, f"start_time {start_time} must be earlier than end_time {end_time}"
        assert isinstance(location_id, str) and location_id and "," not in location_id
        assert isinstance(parameter_id, str) and parameter_id and "," not in parameter_id
        if qualifier_id:
            assert isinstance(qualifier_id, str) and "," not in qualifier_id

        api_call = api_calls.GetTimeSeriesSingle(
            start_time=start_time,
            end_time=end_time,
            location_ids=location_id,
            parameter_ids=parameter_id,
            qualifier_ids=qualifier_id,
            thinning=thinning,
            only_headers=only_headers,
            show_statistics=show_statistics,
            omit_empty_timeseries=omit_empty_timeseries,
            drop_missing_values=drop_missing_values,
            flag_threshold=flag_threshold,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_time_series_multi(
        self,
        output_choice: str,
        #
        start_time: datetime,
        end_time: datetime,
        location_ids: Union[List[str], str] = None,
        parameter_ids: Union[List[str], str] = None,
        qualifier_ids: Union[List[str], str] = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ) -> List[Path]:
        assert start_time < end_time, f"start_time {start_time} must be earlier than end_time {end_time}"
        any_multi = any([isinstance(x, list) and len(x) > 1 for x in (location_ids, parameter_ids, qualifier_ids)])
        assert any_multi
        api_call = api_calls.GetTimeSeriesMulti(
            start_time=start_time,
            end_time=end_time,
            location_ids=location_ids,
            parameter_ids=parameter_ids,
            qualifier_ids=qualifier_ids,
            thinning=thinning,
            only_headers=only_headers,
            show_statistics=show_statistics,
            omit_empty_timeseries=omit_empty_timeseries,
            drop_missing_values=drop_missing_values,
            flag_threshold=flag_threshold,
            #
            output_choice=output_choice,
            retry_backoff_session=self.retry_backoff_session,
        )
        all_file_paths = api_call.run()
        return all_file_paths
