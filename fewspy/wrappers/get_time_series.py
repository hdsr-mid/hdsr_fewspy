from datetime import datetime
from fewspy.time_series import TimeSeriesSet
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews
from typing import List
from typing import Union

import logging
import requests


logger = logging.getLogger(__name__)


def get_time_series(
    url: str,
    document_format: str,
    ssl_verify: bool,
    filter_id: str,
    location_ids: Union[str, List[str]] = None,
    parameter_ids: Union[str, List[str]] = None,
    qualifier_ids: Union[str, List[str]] = None,
    start_time: datetime = None,
    end_time: datetime = None,
    thinning: int = None,
    only_headers: bool = False,
    show_statistics: bool = False,
) -> TimeSeriesSet:
    """Get FEWS qualifiers as a pandas DataFrame.
    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
        - filter_id (str): the FEWS id of the filter to pass as request parameter
        - location_ids (list): list with FEWS location ids to extract timeseries from. Defaults to None.
        - parameter_ids (list): list with FEWS parameter ids to extract timeseries from. Defaults to None.
        - qualifier_ids (list): list with FEWS qualifier ids to extract timeseries from. Defaults to None.
        - start_time (datetime.datetime): datetime-object with start datetime to use in request. Defaults to None.
        - end_time (datetime.datetime): datetime-object with end datetime to use in request. Defaults to None.
        - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
        - only_headers (bool): if True, only headers will be returned. Defaults to False.
        - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".

    """
    report_string = "Headers {status}" if only_headers else "TimeSeries {status}"

    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals())
    response = requests.get(url=url, params=parameters, verify=ssl_verify)
    timer.report(message=report_string.format(status="request"))

    # parse the response
    if response.ok:
        pi_time_series = response.json()
        time_series_set = TimeSeriesSet.from_pi_time_series(pi_time_series)
        timer.report(message=report_string.format(status="parsed"))
        if time_series_set.is_empty:
            logger.debug(f"FEWS WebService request passing empty set: {response.url}")
    else:
        logger.error(f"FEWS WebService request {response.url} responds {response.text}")
        time_series_set = TimeSeriesSet()

    return time_series_set
