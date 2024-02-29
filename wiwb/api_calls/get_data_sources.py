from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from wiwb.api_calls.base import Request
from wiwb.globals import PRIMARY_STRUCTURE_TYPES

import logging
import requests


logger = logging.getLogger(__name__)


@dataclass
class GetDataSources(Request):
    """GetDataSources request"""

    primary_structure_types: PRIMARY_STRUCTURE_TYPES = field(default_factory=lambda: ["Grid"])

    @property
    def url_post_fix(self) -> str:
        return "entity/datasources/get"

    def run(self) -> Dict:
        response = requests.post(self.url, headers=self.auth.headers, json={})

        if response.ok:  # return list of data sources
            return {
                k: v
                for k, v in response.json()["DataSources"].items()
                if v["PrimaryStructureType"] in self.primary_structure_types
            }

        else:  # raise Error
            response.raise_for_status()
