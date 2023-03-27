from fewspy.constants import API_DOCUMENT_FORMAT
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews

import logging
import requests


logger = logging.getLogger(__name__)


def get_timezone_id(
    url: str,
    filter_id: str = None,
    document_format: str = API_DOCUMENT_FORMAT,
) -> str:
    """Get FEWS timezone id.
    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/timezoneid
        - filter_id (str): the FEWS id of the filter to pass as request parameter
    Returns:
        str: timezone string, e.g. GMT+01:00 (expressing a GMT + 1 hour offset)
    """

    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals())
    response = requests.get(url=url, params=parameters)
    timer.report(message="Timezone request")

    # parse the response
    if response.status_code == 200:
        result = response.text
        timer.report(message="Timezone parsed")
    else:
        logger.error(f"FEWS Server responds {response.text}")

    return result
