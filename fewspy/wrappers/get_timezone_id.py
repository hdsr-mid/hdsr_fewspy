from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews

import logging


logger = logging.getLogger(__name__)


def get_timezone_id(
    url: str,
    pi_settings: PiSettings,
    request_settings: RequestSettings,
    retry_backoff_session: RequestsRetrySession,
) -> str:
    """Get FEWS timezone id.
    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/timezoneid
    Returns:
        str: timezone string, e.g. GMT+01:00 (expressing a GMT + 1 hour offset)
    """

    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_settings)
    response = retry_backoff_session.get(url=url, params=parameters, verify=pi_settings.ssl_verify)
    timer.report(message="Timezone request")

    # parse the response
    if response.status_code == 200:
        result = response.text
        timer.report(message="Timezone parsed")
    else:
        logger.error(f"FEWS Server responds {response.text}")

    return result
