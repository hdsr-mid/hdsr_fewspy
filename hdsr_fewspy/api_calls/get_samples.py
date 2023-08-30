from datetime import datetime
from hdsr_fewspy.api_calls.base import GetRequest
from hdsr_fewspy.constants.choices import OutputChoices
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetSamples(GetRequest):
    def __init__(self, start_time: datetime, end_time: datetime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = start_time
        self.end_time = end_time

    @property
    def url_post_fix(self) -> str:
        return "samples"

    @property
    def allowed_request_args(self) -> List[str]:
        return []

    @property
    def required_request_args(self) -> List[str]:
        return []

    @property
    def allowed_output_choices(self) -> List[OutputChoices]:
        return []

    def run(self):
        raise NotImplementedError()
