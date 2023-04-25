from datetime import datetime
from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
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
        return [
            ApiParameters.filter_id,
            ApiParameters.sample_ids,
            ApiParameters.location_ids,
            ApiParameters.parameter_ids,
            ApiParameters.qualifier_ids,
            ApiParameters.start_time,
            ApiParameters.end_time,
            ApiParameters.start_creation_time,
            ApiParameters.end_creation_time,
            ApiParameters.omit_missing,
            ApiParameters.only_headers,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def required_request_args(self) -> List[str]:
        return [
            ApiParameters.filter_id,
            ApiParameters.location_ids,
            ApiParameters.parameter_ids,
            ApiParameters.qualifier_ids,
            ApiParameters.start_time,
            ApiParameters.end_time,
            ApiParameters.omit_missing,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
        ]

    def run(self):
        raise NotImplementedError()
        # response = self.retry_backoff_session.get(
        #     url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        # )
