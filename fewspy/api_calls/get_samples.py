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
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
        ]

    def run(self):
        # do the request
        parameters = parameters_to_fews(parameters=locals(), pi_settings=self.pi_settings)
        response = self.retry_backoff_session.get(url=self.url, params=parameters, verify=self.pi_settings.ssl_verify)

        # parse the response
        raise NotImplementedError
