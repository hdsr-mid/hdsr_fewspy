from fewspy.api_calls.base import GetRequest
from fewspy.utils.transformations import parameters_to_fews

import logging


logger = logging.getLogger(__name__)


class GetTimeZoneId(GetRequest):
    """Get FEWS timezone id.

    Returns: str: timezone string, e.g. GMT+01:00 (expressing a GMT + 1 hour offset)
    """

    url_post_fix = "timezoneid"

    def run(self):
        # do the request
        parameters = parameters_to_fews(parameters=locals(), pi_settings=self.pi_settings)
        response = self.retry_backoff_session.get(url=self.url, params=parameters, verify=self.pi_settings.ssl_verify)

        # parse the response
        if response.status_code != 200:
            logger.error(f"FEWS Server responds {response.text}")
        return response.text
