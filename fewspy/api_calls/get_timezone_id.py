from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import OutputChoices
from typing import List

import logging
import requests


logger = logging.getLogger(__name__)


class GetTimeZoneId(GetRequest):
    """Get FEWS timezone id.

    Returns: str: timezone string, e.g. GMT+01:00 (expressing a GMT + 1 hour offset)
    """

    url_post_fix = "timezoneid"

    def __init__(self, *args, **kwargs):
        # No args here as only args 'documentFormat' and 'documentVersion' are already in GetRequest args
        super().__init__(*args, **kwargs)

    @property
    def whitelist_request_args(self) -> List[str]:
        # sa test page states 'document_format'+'document_version', but those return http code 400 ..
        return []

    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
        ]

    def run(self) -> List[requests.models.Response]:
        # do the request
        response = self.retry_backoff_session.get(
            url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        )
        # parse the response
        if response.status_code != 200:
            logger.error(f"FEWS Server responds {response.text}")
        return [response]
