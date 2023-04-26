from hdsr_fewspy.api_calls.base import GetRequest
from hdsr_fewspy.constants.choices import ApiParameters
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetFilters(GetRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def url_post_fix(self) -> str:
        return "filters"

    @property
    def allowed_request_args(self) -> List[str]:
        return [ApiParameters.filter_id, ApiParameters.document_format, ApiParameters.document_version]

    @property
    def required_request_args(self) -> List[str]:
        return [ApiParameters.filter_id, ApiParameters.document_format, ApiParameters.document_version]

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
        ]

    def run(self) -> ResponseType:
        response = self.retry_backoff_session.get(
            url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        )
        return response
