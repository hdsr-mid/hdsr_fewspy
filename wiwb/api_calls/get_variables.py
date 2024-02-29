from dataclasses import dataclass
from dataclasses import field
from typing import List
from wiwb.api_calls.base import Request

import logging
import requests


logger = logging.getLogger(__name__)


@dataclass
class GetVariables(Request):
    """GetVariables request"""

    data_source_codes: List[str] = field(default_factory=list)
    variable_codes: List[str] = field(default_factory=list)

    @property
    def url_post_fix(self) -> str:
        return "entity/variables/get"

    @property
    def json(self) -> dict:
        return {
            "DataSourceCodes": self.data_source_codes,
            "VariableCodes": self.variable_codes,
        }

    def run(self) -> List[str]:
        response = requests.post(self.url, headers=self.auth.headers, json=self.json)

        if response.ok:  # return list of data sources
            return response.json()["Variables"]

        else:  # raise Error
            response.raise_for_status()
