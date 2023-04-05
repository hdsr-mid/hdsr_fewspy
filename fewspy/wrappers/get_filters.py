from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews
from typing import List

import logging


logger = logging.getLogger(__name__)


def get_filters(
    url: str,
    #
    pi_setttings: PiSettings,
    request_settings: RequestSettings,
    retry_backoff_session: RequestsRetrySession,
    #
) -> List[dict]:
    """Get FEWS qualifiers as a pandas DataFrame.

    Args:
    - url (str): url Delft-FEWS PI REST WebService. For example:
    http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/filters
    Returns:
      df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_setttings)
    response = retry_backoff_session.get(url=url, params=parameters, verify=pi_setttings.ssl_verify)
    timer.report(message="Filters request")

    # parse the response
    result = []
    if response.status_code == 200:
        if "filters" in response.json().keys():
            result = response.json()["filters"]
        timer.report(message="Filters parsed")
    else:
        logger.error(f"FEWS Server responds {response.text}")

    return result
