from datetime import datetime
from fewspy import exceptions
from fewspy import wrappers
from fewspy.constants.choices import TimeZoneChoices
from fewspy.constants.paths import HDSR_FEWSPY_VERSION
from fewspy.constants.pi_settings import pi_settings_production
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import request_settings
from fewspy.constants.request_settings import RequestSettings
from fewspy.permissions import Permissions
from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.bug_report import create_bug_report_when_error
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import logging
import pandas as pd
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = logging.getLogger(__name__)


class Api:
    """Python API for the Deltares FEWS PI REST Web Service.

    The methods corresponding with the FEWS PI-REST requests (see Deltares website). For more info on how to work
    with the FEWS REST Web Service, visit the Deltares website:
    https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service

    Example: api = Api(base_url='http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/')
    """

    def __init__(
        self,
        email: str,
        hdsr_fewspy_token: str,
        pi_settings: PiSettings = pi_settings_production,
        output_folder: Path = Path("1"),
    ):
        self.permissions = Permissions(email=email, hdsr_fewspy_token=hdsr_fewspy_token)
        self.pi_settings = self._validate_pi_settings(pi_settings=pi_settings)
        self.request_settings: RequestSettings = request_settings
        self.retry_backoff_session = RequestsRetrySession(self.request_settings, pi_settings=self.pi_settings)
        self.ensure_service_is_running()
        self.hdsr_fewspy_version = HDSR_FEWSPY_VERSION

    @create_bug_report_when_error
    def ensure_service_is_running(self) -> None:
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
            raise exceptions.StandAloneFewsWebServiceNotRunningError(message=msg, errors=response.text)
        raise exceptions.FewsWebServiceNotRunningError(message=msg, errors=response.text)

    def _validate_pi_settings(self, pi_settings: PiSettings) -> PiSettings:
        assert isinstance(
            pi_settings, PiSettings
        ), "pi_settings must be a PiSettings, see README.ml example how to create one"
        mapper = {
            "domain": (pi_settings.domain, self.permissions.allowed_domain),
            "module_instance_id": (pi_settings.module_instance_ids, self.permissions.allowed_module_instance_id),
            "timezone": (pi_settings.time_zone, TimeZoneChoices.get_all()),
            "filter_id": (pi_settings.filter_ids, self.permissions.allowed_filter_id),
            "service": (pi_settings.service, self.permissions.allowed_service),
        }
        for setting, used_allowed in mapper.items():
            used, allowed = used_allowed
            assert isinstance(allowed, list), f"code error, {allowed} must be a list"
            if used in allowed:
                continue
            raise exceptions.PiSettingsError(message=f"{setting} has {used} which is not in allowed {allowed}")
        return pi_settings

    def _get_kwargs_for_wrapper(self, url_post_fix: str, kwargs: dict) -> dict:
        """Update kwargs for wrapped function."""
        kwargs = {
            **kwargs,
            **dict(
                url=f"{self.pi_settings.base_url}{url_post_fix}",
                pi_settings=self.pi_settings,
                request_settings=self.request_settings,
                retry_backoff_session=self.retry_backoff_session,
            ),
        }
        kwargs.pop("self")
        kwargs.pop("parallel", None)
        return kwargs

    @create_bug_report_when_error
    def get_parameters(self) -> pd.DataFrame:
        """Get FEWS parameters as a pandas DataFrame."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="parameters", kwargs=locals())
        result = wrappers.get_parameters(**kwargs)
        return result

    @create_bug_report_when_error
    def get_filters(self) -> List[Dict]:
        """Get FEWS filters as a list with dictionaries."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="filters", kwargs=locals())
        result = wrappers.get_filters(**kwargs)
        return result

    @create_bug_report_when_error
    def get_locations(self, attributes: list = None):
        """Get FEWS locations as a geopandas GeoDataFrame.
        Args:
            - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
        Returns:
            gpd (geopandas.GeoDataFrame): GeoDataFrame with index "id" and columns "name" and "group_id".
        """
        attributes = attributes if attributes else []
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="locations", kwargs=locals())
        result = wrappers.get_locations(**kwargs)
        return result

    @create_bug_report_when_error
    def get_qualifiers(self) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame

        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="qualifiers/", kwargs=locals())
        return wrappers.get_qualifiers(**kwargs)

    @create_bug_report_when_error
    def get_timezone_id(self) -> str:
        """Get FEWS timezone_id the FEWS API is running on."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="timezoneid/", kwargs=locals())
        return wrappers.get_timezone_id(**kwargs)

    @create_bug_report_when_error
    def get_samples(self, start_time, end_time) -> pd.DataFrame:
        """Get FEWS samples as a pandas DataFrame."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="samples/", kwargs=locals())
        return wrappers.get_samples(**kwargs)

    @create_bug_report_when_error
    def get_time_series(
        self,
        start_time: datetime,
        end_time: datetime,
        omit_empty_timeseries: bool = True,
        location_ids: Union[str, List[str]] = None,
        parameter_ids: Union[str, List[str]] = None,
        qualifier_ids: Union[str, List[str]] = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ):
        """Get FEWS qualifiers as a pandas DataFrame.

        Args:
            - filter_id (str): the FEWS id of the filter to pass as request parameter.
            - start_time (datetime.datetime): datetime-object with start datetime to use in request.
            - end_time (datetime.datetime): datetime-object with end datetime to use in request.
            - omit_empty_timeseries (bool): if True, missing values (-999.0) are left out in response. Defaults to True
            - location_ids (list): list with FEWS location ids to extract timeseries from. Defaults to None.
            - parameter_ids (list): list with FEWS parameter ids to extract timeseries from. Defaults to None.
            - qualifier_ids (list): list with FEWS qualifier ids to extract timeseries from. Defaults to None.
            - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
            - only_headers (bool): if True, only headers will be returned. Defaults to False.
            - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
            - drop_missing_values (bool): Defaults to False.
            - flag_threshold (int): Exclude unreliable values. Default to 6 (meaning flags >= 6 will be excluded).
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        assert start_time < end_time, f"start '{start_time}' must be before end_time {end_time}"
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="timeseries/", kwargs=locals())
        result = wrappers.get_time_series(**kwargs)
        return result
