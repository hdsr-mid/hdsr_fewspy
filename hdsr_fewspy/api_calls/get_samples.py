from datetime import datetime
from hdsr_fewspy.api_calls.base import GetRequest
from hdsr_fewspy.constants.choices import ApiParameters
from hdsr_fewspy.constants.choices import OutputChoices
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetSamples(GetRequest):

    def __init__(
        self, start_time: datetime, end_time: datetime, location_ids: str = None, sample_ids=None, *args, **kwargs
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.location_ids = location_ids
        self.sample_ids = sample_ids
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        if self.location_ids is not None:
            is_valid = isinstance(self.location_ids, str) and self.location_ids and "," not in self.location_ids
            assert is_valid, f"location_id '{self.location_ids}' must be a string (one location)"
        if self.sample_ids is not None:
            is_valid = isinstance(self.sample_ids, str) and self.sample_ids and "," not in self.sample_ids
            assert is_valid, f"sample_id '{self.sample_ids}'must be a string (one sample)"

        if sum([bool(self.location_ids), bool(self.sample_ids)]) == 0:
            raise AssertionError("Use at least one of the two (location_id and/or sample_id)")

    @property
    def url_post_fix(self) -> str:
        return "samples"

    @property
    def allowed_request_args(self) -> List[str]:
        return [
            ApiParameters.location_ids,
            ApiParameters.sample_ids,
            ApiParameters.parameter_ids,
            ApiParameters.start_time,
            ApiParameters.end_time,
            ApiParameters.filter_id,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def required_request_args(self) -> List[str]:
        return [
            ApiParameters.start_time,
            ApiParameters.end_time,
            ApiParameters.filter_id,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def allowed_output_choices(self) -> List[OutputChoices]:
        return [
            OutputChoices.xml_response_in_memory,
        ]

    def run(self):
        response = self.retry_backoff_session.get(
            url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        )
        # parse the response to dataframe
        if response.status_code != 200:
            logger.error(f"FEWS Server responds {response.text}")
        return response
