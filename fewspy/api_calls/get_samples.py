from datetime import datetime
from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import OutputChoices
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetSamples(GetRequest):
    """Get FEWS samples."""

    url_post_fix = "samples"

    def __init__(self, start_time: datetime, end_time: datetime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = start_time
        self.end_time = end_time

    @property
    def whitelist_request_args(self) -> List[str]:
        raise NotImplementedError("fill this list")

    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
        ]

    def run(self):
        raise NotImplementedError()
