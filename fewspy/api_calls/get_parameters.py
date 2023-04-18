from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
from fewspy.utils.conversions import camel_to_snake_case
from typing import List

import logging
import pandas as pd


logger = logging.getLogger(__name__)

COLUMNS = [
    "id",
    "name",
    "parameter_type",
    "unit",
    "display_unit",
    "uses_datum",
    "parameter_group",
]


class GetParameters(GetRequest):
    def __init__(self, show_attributes: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_attributes = show_attributes

    @property
    def url_post_fix(self) -> str:
        return "parameters"

    @property
    def allowed_request_args(self) -> List[str]:
        return [
            ApiParameters.filter_id,
            ApiParameters.show_attributes,
            ApiParameters.document_format,
            ApiParameters.document_version,
        ]

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self) -> pd.DataFrame:
        raise NotImplementedError
        # response = self.retry_backoff_session.get(
        #     url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        # )
        #
        # # parse the response
        # df = pd.DataFrame(columns=COLUMNS)
        # if response.status_code == 200:
        #     if "timeSeriesParameters" in response.json().keys():
        #         df = pd.DataFrame(response.json()["timeSeriesParameters"])
        #         df.columns = [camel_to_snake_case(i) for i in df.columns]
        #         df["uses_datum"] = df["uses_datum"] == "true"
        #
        # else:
        #     logger.error(f"FEWS Server responds {response.text}")
        #
        # df.set_index("id", inplace=True)
        #
        # return df
