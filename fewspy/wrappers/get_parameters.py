from fewspy.retry_session import RequestsRetrySession
from fewspy.utils.conversions import camel_to_snake_case
from fewspy.utils.timer import Timer
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
    url: str, document_format: str, ssl_verify: bool, retry_backoff_session: RequestsRetrySession, filter_id: str = None
) -> pd.DataFrame:
    """Get FEWS qualifiers as a pandas DataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService.
          e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
        - filter_id (str): the FEWS id of the filter to pass as request parameter
        - document_format (str): request document format to return. Defaults to PI_JSON.
        - verify (bool, optional): passed to requests.get verify parameter. Defaults to False.
    Returns:
        df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """
    # do the request
    timer = Timer()
    parameters = parameters_to_fews(parameters=locals())
    response = retry_backoff_session.get(url, parameters=parameters, verify=ssl_verify)
    timer.report(message="Parameters request")

    # parse the response
    df = pd.DataFrame(columns=COLUMNS)
    if response.status_code == 200:
        if "timeSeriesParameters" in response.json().keys():
            df = pd.DataFrame(response.json()["timeSeriesParameters"])
            df.columns = [camel_to_snake_case(i) for i in df.columns]
            df["uses_datum"] = df["uses_datum"] == "true"
            timer.report(message="Parameters parsed")
    else:
        logger.error(f"FEWS Server responds {response.text}")

    df.set_index("id", inplace=True)

    return df
