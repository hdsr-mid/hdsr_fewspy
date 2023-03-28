from enum import Enum
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).parent.parent.parent
assert BASE_DIR.name == "hdsr_fewspy", f"BASE_DIR must be hdsr_fewspy, but is {BASE_DIR.name}"


class PiRestDocumentFormatChoices(Enum):
    json = "PI_JSON"
    # xml = "PI_XML"

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]


class TimeZoneChoices(Enum):
    gmt = "Etc/GMT"
    gmt_0 = "Etc/GMT-0"
    eu_amsterdam = "Europe/Amsterdam"

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]


class ApiKeys:

    start_time = "start_time"
    end_time = "end_time"
    document_format = "document_format"
    document_version = "document_version"
    filter_id = "filter_id"
    include_location_relations = "include_location_relations"
    location_ids = "location_ids"
    only_headers = "only_headers"
    parameter_ids = "parameter_ids"
    qualifier_ids = "qualifier_ids"
    attributes = "attributes"
    show_statistics = "show_statistics"
    thinning = "thinning"
    omit_empty_timeseries = "omit_empty_timeSeries"
