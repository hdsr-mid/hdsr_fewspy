from fewspy.api_calls.base import GetRequest
from fewspy.utils.transformations import parameters_to_fews

import logging


logger = logging.getLogger(__name__)


class GetFilters(GetRequest):
    """Get FEWS filters as a pandas DataFrame.

    Args:
        - url (str): url Delft-FEWS PI REST WebService. For example:
        http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/filters
    Returns:
        - df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
    """

    url_post_fix = "filters"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        # do the request
        parameters = parameters_to_fews(parameters=locals(), pi_settings=self.pi_settings)
        response = self.retry_backoff_session.get(url=self.url, params=parameters, verify=self.pi_settings.ssl_verify)

        # parse the response
        result = []
        if response.status_code == 200:
            if "filters" in response.json().keys():
                result = response.json()["filters"]
        else:
            logger.error(f"FEWS Server responds {response.text}")

        return result
