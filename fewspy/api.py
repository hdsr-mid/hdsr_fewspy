from datetime import datetime
from fewspy import api_calls
from fewspy import exceptions
from fewspy.constants.choices import OutputChoices
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

    The methods corresponding with the FEWS PI-REST requests (see Deltares website). For more info on how to work
    with the FEWS REST Web Service, visit the Deltares website:
    https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service

    Example: api = Api(base_url='http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/')
    """

    def __init__(
        self,
        pi_settings: PiSettings = pi_settings_production,
        output_choice: str = OutputChoices.json_response_in_memory,
        output_directory: Union[str, Path] = None,
        hdsr_fewspy_email: str = None,
        hdsr_fewspy_token: str = None,
    ):
        self.permissions = Permissions(hdsr_fewspy_email=hdsr_fewspy_email, hdsr_fewspy_token=hdsr_fewspy_token)
        self.output_choice: str = self._validate_output_choice(output_choice=output_choice)
        self.output_directory: Path = self._validate_output_directory(output_directory=output_directory)
        self.pi_settings = self._validate_pi_settings(pi_settings=pi_settings)
        self.request_settings: RequestSettings = default_request_settings
        self.retry_backoff_session = RetryBackoffSession(
            _request_settings=self.request_settings,
            pi_settings=self.pi_settings,
            output_choice=self.output_choice,
            output_directory=self.output_directory,
        )
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

    @staticmethod
    def _validate_output_choice(output_choice: str) -> str:
        assert output_choice and isinstance(
            output_choice, str
        ), f"output_choice {output_choice} must be non empty string"
        if output_choice in OutputChoices.get_all():
            return output_choice
        raise AssertionError(f"output_choice '{output_choice}' must be in {OutputChoices.get_all()}")

    def _validate_output_directory(self, output_directory: Union[str, Path]) -> Optional[Path]:
        is_output_dir_needed = OutputChoices.is_output_dir_needed(output_choice=self.output_choice)

        # scenario 1: no output_dir needed
        if not is_output_dir_needed:
            if output_directory:
                logger.warning(
                    f"you specified a output_directory '{output_directory}' but we will not need it as "
                    f"output_choice='{self.output_choice}'. Setting output_directory to None"
                )
            return None

        # scenario 2: output_dir needed
        assert output_directory, f"Please specify a output_directory as output_choice='{self.output_choice}'"
        output_directory = Path(output_directory)
        assert output_directory.is_dir(), f"output_directory {output_directory} must exist"
        is_dir_writable = os.access(path=output_directory.as_posix(), mode=os.W_OK)
        assert is_dir_writable, f"output_directory {output_directory} must be writable"

        datetime_foldername = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_directory = output_directory / datetime_foldername

        # TODO: enable this before release
        # output_directory.mkdir(parents=False, exist_ok=False)

        logger.info(f"created output_directory {output_directory}")
        return output_directory

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
        for setting, value in mapper.items():
            used, allowed = value
            assert isinstance(allowed, list), f"code error, {allowed} must be a list"
            if used in allowed:
                continue
            raise exceptions.PiSettingsError(message=f"{setting} has {used} which is not in allowed {allowed}")

        # set document_format
        valid_document_format = OutputChoices.get_pi_rest_document_format(output_choice=self.output_choice)
        if pi_settings.document_format != valid_document_format:
            msg = (
                f"set pi_settings.document_format to '{valid_document_format}' since output_choice "
                f"is '{self.output_choice}'"
            )
            logger.info(msg)
            pi_settings.document_format = valid_document_format

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

    # @create_bug_report_when_error
    def get_parameters(self) -> pd.DataFrame:
        """Get FEWS parameters as a pandas DataFrame."""
        api_call = api_calls.GetParameters(retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_filters(self) -> List[Dict]:
        """Get FEWS filters as a list with dictionaries."""
        api_call = api_calls.GetFilters(retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_locations(self, attributes: list = None):
        """Get FEWS locations as a geopandas GeoDataFrame.
        Args:
            - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
        Returns:
            gpd (geopandas.GeoDataFrame): GeoDataFrame with index "id" and columns "name" and "group_id".
        """
        attributes = attributes if attributes else []
        api_call = api_calls.GetLocations(attributes=attributes, retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_qualifiers(self) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame

        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        api_call = api_calls.GetQualifiers(retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_timezone_id(self) -> str:
        """Get FEWS timezone_id the FEWS API is running on."""
        api_call = api_calls.GetTimeZoneId(retry_backoff_session=self.retry_backoff_session)
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_samples(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Get FEWS samples as a pandas DataFrame."""
        api_call = api_calls.GetSamples(
            start_time=start_time, end_time=end_time, retry_backoff_session=self.retry_backoff_session
        )
        result = api_call.run()
        return result

    # @create_bug_report_when_error
    def get_time_series(
        self,
        start_time: datetime,
        end_time: datetime,
        location_ids: Union[str, List[str]] = None,
        parameter_ids: Union[str, List[str]] = None,
        qualifier_ids: Union[str, List[str]] = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
    ) -> pd.DataFrame:
        """
        Note that if you specify >1 location_ids and/or parameter_ids and/or qualifier_ids, then you also need to
        specify a output_directory.
        """
        # detect run mode
        any_multi = any([isinstance(x, list) and len(x) > 1 for x in (location_ids, parameter_ids, qualifier_ids)])
        if any_multi:
            logger.info(f"found >1 locations/parameters/qualifiers, so we run GetTimeSeriesMulti")
            klass = api_calls.GetTimeSeriesMulti
        else:
            logger.info(f"found <=1 location/parameter/qualifier so we run GetTimeSeriesSingle")
            klass = api_calls.GetTimeSeriesSingle

        api_call = klass(
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
            retry_backoff_session=self.retry_backoff_session,
        )
        result = api_call.run()
        return result
