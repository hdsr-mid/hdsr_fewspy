from fewspy.constants import API_DOCUMENT_FORMAT
from fewspy.daniel.src.fewspy.wrappers import get_filters
from fewspy.daniel.src.fewspy.wrappers import get_locations
from fewspy.daniel.src.fewspy.wrappers import get_parameters
from fewspy.daniel.src.fewspy.wrappers import get_qualifiers
from fewspy.daniel.src.fewspy.wrappers import get_time_series
from fewspy.daniel.src.fewspy.wrappers import get_time_series_async
from fewspy.daniel.src.fewspy.wrappers import get_timezone_id
from fewspy.expections import URLNotFoundError
from fewspy.daniel.src.fewspy.utils.timer import Timer

import logging
import pandas as pd
import requests
import urllib3


LOGGER = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Api:
    """Python API for the Deltares FEWS PI REST Web Service.

    The methods corresponding with the FEWS PI-REST requests (see Deltares website). For more info on how to work
    with the FEWS REST Web Service, visit the Deltares website:
    https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service
    """

    def __init__(self, base_url, logger=None, ssl_verify: bool = False):
        self.document_format: str = API_DOCUMENT_FORMAT
        self.base_url = self._validate_base_url(base_url=base_url)
        self.ssl_verify = True
        self.timer = Timer(logger)

    @staticmethod
    def _determine_ssl_verify():
        # # set ssl_verify
        # if ssl_verify is None:
        #     self.ssl_verify = verify
        # else:
        #     self.ssl_verify = ssl_verify
        #
        # # estimate ssl_verify
        # if not ssl_verify:
        #     ssl_verify = True if base_url.startswith("https") else False
        ssl_verify = True

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        base_url = f"{base_url}/" if not base_url.endswith("/") else base_url
        response = requests.get(url=base_url, verify=False)
        if response.ok:
            return base_url
        raise URLNotFoundError(message=f"{base_url} is not a root to a live FEWS PI Rest WebService")

    def __kwargs(self, url_post_fix: str, kwargs: dict) -> dict:
        kwargs = {
            **kwargs,
            **dict(
                url=f"{self.base_url}{url_post_fix}",
                document_format=self.document_format,
                verify=self.ssl_verify,
            ),
        }
        kwargs.pop("self")
        kwargs.pop("parallel", None)
        return kwargs

    def get_parameters(self, filter_id=None):
        """Get FEWS qualifiers as a pandas DataFrame
        Args:
            filter_id (str): the FEWS id of the filter to pass as request parameter
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self.__kwargs(url_post_fix="parameters", kwargs=locals())
        result = get_parameters(**kwargs)
        return result

    def get_filters(self, filter_id=None):
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            filter_id (str): the FEWS id of the filter to pass as request parameter
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self.__kwargs(url_post_fix="filters", kwargs=locals())
        result = get_filters(**kwargs)
        return result

    def get_locations(self, filter_id=None, attributes=[]):
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            - filter_id (str): the FEWS id of the filter to pass as request parameter
            - attributes (list): if not emtpy, the location attributes to include as columns in the pandas DataFrame.
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self.__kwargs(url_post_fix="locations", kwargs=locals())
        result = get_locations(**kwargs)
        return result

    def get_qualifiers(self) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame

        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        url = f"{self.base_url}qualifiers"
        result = get_qualifiers(url, verify=self.ssl_verify)
        return result

    def get_timezone_id(self) -> str:
        """Get FEWS timezone_id the FEWS API is running on."""
        url = f"{self.base_url}timezoneid"
        result = get_timezone_id(url, verify=self.ssl_verify)
        return result

    def get_time_series(
        self,
        filter_id,
        location_ids=None,
        parameter_ids=None,
        qualifier_ids=None,
        start_time=None,
        end_time=None,
        thinning=None,
        only_headers=False,
        show_statistics=False,
        parallel=False,
    ):
        """Get FEWS qualifiers as a pandas DataFrame.

        Args:
            - filter_id (str): the FEWS id of the filter to pass as request parameter
            - location_ids (list): list with FEWS location ids to extract timeseries from. Defaults to None.
            - parameter_ids (list): list with FEWS parameter ids to extract timeseries from. Defaults to None.
            - qualifier_ids (list): list with FEWS qualifier ids to extract timeseries from. Defaults to None.
            - start_time (datetime.datetime): datetime-object with start datetime to use in request. Defaults to None.
            - end_time (datetime.datetime): datetime-object with end datetime to use in request. Defaults to None.
            - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
            - only_headers (bool): if True, only headers will be returned. Defaults to False.
            - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
            - parallel (bool): if True, timeseries are requested by the asynchronous wrapper. Defaults to False
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        kwargs = self.__kwargs(url_post_fix="timeseries", kwargs=locals())
        if parallel:
            kwargs.pop("only_headers")
            kwargs.pop("show_statistics")
            result = get_time_series_async(**kwargs)
        else:
            result = get_time_series(**kwargs)
        return result
