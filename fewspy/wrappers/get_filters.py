from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews
from typing import List

import logging
import requests


logger = logging.getLogger(__name__)


def get_filters(
    url: str,
    document_format: str,
    ssl_verify: bool,
    filter_id: str = None,
) -> List[dict]:
    """Get FEWS qualifiers as a pandas DataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService. For example:
          http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/filters
        - document_format (str): request document format to return. Defaults to PI_JSON.
        - filter_id (str): the FEWS id of the filter to pass as request parameter
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals())
    response = requests.get(url, parameters, verify=True)
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
