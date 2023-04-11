from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.conversions import camel_to_snake_case
from fewspy.utils.transformations import parameters_to_fews

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


def get_parameters(
    url: str,
    #
    pi_setttings: PiSettings,
    request_settings: RequestSettings,
    retry_backoff_session: RequestsRetrySession,
) -> pd.DataFrame:
    """Get FEWS parameters as a pandas DataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_setttings)
    response = retry_backoff_session.get(url, parameters=parameters, verify=pi_setttings.ssl_verify)

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
