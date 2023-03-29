from enum import Enum
from typing import List


class PiRestDocumentFormatChoices(Enum):
    xml = "PI_XML"
    json = "PI_JSON"

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]


class TimeZoneChoices(Enum):
    gmt = 0.0  # "Etc/GMT"
    gmt_0 = 0.0  # "Etc/GMT-0"
    eu_amsterdam = 1.0  # "Europe/Amsterdam"

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]

    @classmethod
    def date_string_format(cls) -> str:
        return "%Y-%m-%dT%H:%M:%SZ"


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
