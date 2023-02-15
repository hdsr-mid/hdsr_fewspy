from fewspy.constants import API_DOCUMENT_FORMAT
from fewspy.daniel.src.fewspy.utils.timer import Timer
from fewspy.daniel.src.fewspy.utils.transformations import parameters_to_fews
from typing import List

import logging
import requests


logger = logging.getLogger(__name__)


def get_filters(
    url: str,
    filter_id: str = None,
    document_format: str = API_DOCUMENT_FORMAT,
    verify: bool = False,
) -> List[dict]:
    """Get FEWS qualifiers as a pandas DataFrame.
    Args:
        url (str): url Delft-FEWS PI REST WebService.
        E.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/filters
        filter_id (str): the FEWS id of the filter to pass as request parameter
        document_format (str): request document format to return. Defaults to PI_JSON.
        verify (bool, optional): passed to requests.get verify parameter.
        Defaults to False.
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer(logger)
    parameters = parameters_to_fews(parameters=locals())
    response = requests.get(url, parameters, verify=verify)
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
