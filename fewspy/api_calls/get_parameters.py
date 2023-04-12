from fewspy.api_calls.base import GetRequest
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
    """Get FEWS parameters as a pandas DataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """

    url_post_fix = "parameters"

    def __init__(self, attributes: List = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = attributes

    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self) -> pd.DataFrame:
        # do the request
        parameters = parameters_to_fews(parameters=locals(), pi_settings=self.pi_settings)
        response = self.retry_backoff_session.get(self.url, parameters=parameters, verify=self.pi_settings.ssl_verify)

        # parse the response
        df = pd.DataFrame(columns=COLUMNS)
        if response.status_code == 200:
            if "timeSeriesParameters" in response.json().keys():
                df = pd.DataFrame(response.json()["timeSeriesParameters"])
                df.columns = [camel_to_snake_case(i) for i in df.columns]
                df["uses_datum"] = df["uses_datum"] == "true"

        else:
            logger.error(f"FEWS Server responds {response.text}")

        df.set_index("id", inplace=True)

        return df
