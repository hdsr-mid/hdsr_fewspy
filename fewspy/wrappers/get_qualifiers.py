from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from typing import Tuple
from xml.etree import ElementTree

import logging
import pandas as pd


logger = logging.getLogger(__name__)


NS = "{http://www.wldelft.nl/fews/PI}"
COLUMNS = ["id", "name", "group_id"]


class GetQualifiers:
    @classmethod
    def get_qualifiers(
        cls,
        url: str,
        pi_settings: PiSettings,
        request_settings: RequestSettings,
        retry_backoff_session: RequestsRetrySession,
    ) -> pd.DataFrame:
        """Get FEWS qualifiers as Pandas DataFrame.
        Args:
            - url (str): url Delft-FEWS PI REST WebService.
              e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
            - verify (bool, optional): passed to requests.get verify parameter. Defaults to False.
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".
        """
        # do the request
        response = retry_backoff_session.get(url=url, verify=pi_settings.ssl_verify)

        # parse the response
        if response.status_code == 200:
            tree = ElementTree.fromstring(response.content)
            qualifiers_tree = [i for i in tree.iter(tag=f"{NS}qualifier")]
            qualifiers_tuple = (cls._element_to_tuple(i) for i in qualifiers_tree)
            df = pd.DataFrame(qualifiers_tuple, columns=COLUMNS)
        else:
            logger.error(f"FEWS Server responds {response.text}")
            df = pd.DataFrame(columns=COLUMNS)
        df.set_index("id", inplace=True)

        return df

    @classmethod
    def _element_to_tuple(cls, qualifier_element: ElementTree.Element) -> Tuple:
        """Parses a qualifier element to a tuple.
        Args:
            - qualifier_element (xml.etree.ElementTree.Element): ET.Element with Delft-FEWS qualifier tags.
        Returns:
            tuple: qualifier properties (id, name, group_id). If not present they will be None.
        """

        def __get_text(element):
            return element.text if element is not None else element

        ident = qualifier_element.get("id")
        name = __get_text(element=next(qualifier_element.iter(tag=f"{NS}name"), None))
        group_id = __get_text(element=next(qualifier_element.iter(tag=f"{NS}groupId"), None))

        return ident, name, group_id
