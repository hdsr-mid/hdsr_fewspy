from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
from typing import List
from typing import Tuple
from xml.etree import ElementTree

import logging
import pandas as pd


logger = logging.getLogger(__name__)


NS = "{http://www.wldelft.nl/fews/PI}"
COLUMNS = ["id", "name", "group_id"]


class GetQualifiers(GetRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def url_post_fix(self) -> str:
        return "qualifiers"

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    @property
    def allowed_request_args(self) -> List[str]:
        return [ApiParameters.show_attributes, ApiParameters.document_format, ApiParameters.document_version]

    def run(self) -> pd.DataFrame:
        raise NotImplementedError
        # response = self.retry_backoff_session.get(
        #     url=self.url, params=self.filtered_fews_parameters, verify=self.pi_settings.ssl_verify
        # )
        # # parse the response
        # if response.status_code == 200:
        #     tree = ElementTree.fromstring(response.content)
        #     qualifiers_tree = [i for i in tree.iter(tag=f"{NS}qualifier")]
        #     qualifiers_tuple = (self._element_to_tuple(i) for i in qualifiers_tree)
        #     df = pd.DataFrame(qualifiers_tuple, columns=COLUMNS)
        # else:
        #     logger.error(f"FEWS Server responds {response.text}")
        #     df = pd.DataFrame(columns=COLUMNS)
        # df.set_index("id", inplace=True)
        #
        # return df

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
