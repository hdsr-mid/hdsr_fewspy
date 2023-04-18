from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
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
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self):
        raise NotImplementedError
        # response = self.retry_backoff_session.get(
        #     url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        # )
        #
        # # parse the response
        # result = []
        # if response.status_code == 200:
        #     if "filters" in response.json().keys():
        #         result = response.json()["filters"]
        # else:
        #     logger.error(f"FEWS Server responds {response.text}")
        #
        # return result
