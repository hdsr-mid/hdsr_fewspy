from datetime import datetime
from fewspy import wrappers
from fewspy.constants.pi_settings import pi_settings_production
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import request_settings
from fewspy.constants.request_settings import RequestSettings
from fewspy.exceptions import URLNotFoundError
from fewspy.retry_session import RequestsRetrySession
from typing import List
from typing import Union

import pandas as pd
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Api:
    """Python API for the Deltares FEWS PI REST Web Service.

    The methods corresponding with the FEWS PI-REST requests (see Deltares website). For more info on how to work
    with the FEWS REST Web Service, visit the Deltares website:
    https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service

    Example: api = Api(base_url='http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/')
    """

    def __init__(
        self,
        base_url: str = None,
        pi_settings: PiSettings = pi_settings_production,
    ):
        self.base_url = self._validate_base_url(base_url=base_url if base_url else pi_settings.base_url)
        self.pi_settings = pi_settings
        self.request_settings: RequestSettings = request_settings
        self.retry_backoff_session = RequestsRetrySession(self.request_settings, pi_settings=self.pi_settings)

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        base_url = f"{base_url}/" if not base_url.endswith("/") else base_url
        response = requests.get(url=base_url, verify=True)
        if response.ok:
            return base_url
        raise URLNotFoundError(message=f"{base_url} is not a root to a live FEWS PI Rest WebService")

    def _get_kwargs_for_wrapper(self, url_post_fix: str, kwargs: dict) -> dict:
        """Update kwargs for wrapped function

        For example:
            from this {
                'end_time': datetime.datetime(2022, 5, 2, 0, 0),
                'filter_id': 'INTERNAL-API',
                'location_ids': ['OW433001'],
                'only_headers': False,
                'parameter_ids': ['H.G.0'],
                'qualifier_ids': None,
                'self': <fewspy.api.Api object at 0x000001F76CD1A0C8>,
                'show_statistics': False,
                'start_time': datetime.datetime(2022, 5, 1, 0, 0),
                'thinning': None
                }
            to this {
                'document_format': 'PI_JSON',
                'end_time': datetime.datetime(2022, 5, 2, 0, 0),
                'filter_id': 'INTERNAL-API',
                'location_ids': ['OW433001'],
                'only_headers': False,
                'parameter_ids': ['H.G.0'],
                'qualifier_ids': None,
                'show_statistics': False,
                'ssl_verify': True,
                'start_time': datetime.datetime(2022, 5, 1, 0, 0),
                'thinning': None,
                'url': 'http://xx:9999//rest/fewspiservice/v1/timeseries'
                }
        """
        kwargs = {
            **kwargs,
            **dict(
                url=f"{self.base_url}{url_post_fix}",
                document_format=self.pi_settings.document_format,
                ssl_verify=self.pi_settings.ssl_verify,
            ),
        }
        kwargs.pop("self")
        kwargs.pop("parallel", None)
        kwargs["retry_backoff_session"] = self.retry_backoff_session
        return kwargs

    def get_parameters(self, filter_id=None):
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            filter_id (str): the FEWS id of the filter to pass as request parameter
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="parameters", kwargs=locals())
        result = wrappers.get_parameters(**kwargs)
        return result

    def get_filters(self, filter_id=None):
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            filter_id (str): the FEWS id of the filter to pass as request parameter
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="filters", kwargs=locals())
        result = wrappers.get_filters(**kwargs)
        return result

    def get_locations(self, filter_id=None, attributes: list = None):
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            - filter_id (str): the FEWS id of the filter to pass as request parameter
            - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        attributes = attributes if attributes else []
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="locations", kwargs=locals())
        result = wrappers.get_locations(**kwargs)
        return result

    def get_qualifiers(self) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame

        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="qualifiers/", kwargs=locals())
        return wrappers.get_qualifiers(**kwargs)

    def get_timezone_id(self) -> str:
        """Get FEWS timezone_id the FEWS API is running on."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="timezoneid/", kwargs=locals())
        return wrappers.get_timezone_id(**kwargs)

    def get_samples(self, start_time, end_time) -> pd.DataFrame:
        """Get FEWS samples as a pandas DataFrame."""
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="samples/", kwargs=locals())
        return wrappers.get_samples(**kwargs)

    def get_time_series(
        self,
        filter_id: str,
        start_time: datetime,
        end_time: datetime,
        location_ids: Union[str, List[str]] = None,
        parameter_ids: Union[str, List[str]] = None,
        qualifier_ids: Union[str, List[str]] = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
    ):
        """Get FEWS qualifiers as a pandas DataFrame.

        Args:
            - filter_id (str): the FEWS id of the filter to pass as request parameter.
            - start_time (datetime.datetime): datetime-object with start datetime to use in request.
            - end_time (datetime.datetime): datetime-object with end datetime to use in request.
            - location_ids (list): list with FEWS location ids to extract timeseries from. Defaults to None.
            - parameter_ids (list): list with FEWS parameter ids to extract timeseries from. Defaults to None.
            - qualifier_ids (list): list with FEWS qualifier ids to extract timeseries from. Defaults to None.
            - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
            - only_headers (bool): if True, only headers will be returned. Defaults to False.
            - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self._get_kwargs_for_wrapper(url_post_fix="timeseries/", kwargs=locals())
        # start_time
        # assert start_time and  < xml_end_max_today
        # uuid = RedisOuterKeys.uuid(row=row)
        # date_range_frequency = self.pi_rest.settings.default_request_period
        # request_date_ranges, date_range_frequency = self._create_date_ranges(
        #     startdate_obj=xml_start,
        #     enddate_obj=xml_end_max_today,
        #     frequency=date_range_frequency,
        # )
        result = wrappers.get_time_series(**kwargs)
        return result
