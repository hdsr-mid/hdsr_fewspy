from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews

import logging


logger = logging.getLogger(__name__)


def get_timezone_id(
    url: str,
    document_format: str,
    ssl_verify: bool,
    retry_backoff_session: RequestsRetrySession,
    filter_id: str = None,
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
    response = retry_backoff_session.get(url=url, params=parameters, verify=ssl_verify)
    timer.report(message="Timezone request")

    # parse the response
    if response.status_code == 200:
        result = response.text
        timer.report(message="Timezone parsed")
    else:
        logger.error(f"FEWS Server responds {response.text}")

    return result
