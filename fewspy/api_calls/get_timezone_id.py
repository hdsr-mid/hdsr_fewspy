from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import OutputChoices
from fewspy.constants.custom_types import ResponseType
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetTimeZoneId(GetRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def url_post_fix(self) -> str:
        return "timezoneid"

    @property
    def allowed_request_args(self) -> List[str]:
        # sa test page states 'document_format'+'document_version', but those return http code 400 ..
        return []

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
        ]

    def run(self) -> List[ResponseType]:
        response = self.retry_backoff_session.get(
            url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        )
        # parse the response
        if response.status_code != 200:
            logger.error(f"FEWS Server responds {response.text}")
        return [response]
