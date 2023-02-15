from enum import Enum
from pathlib import Path


# BASE_DIR avoid 'Path.cwd()', as wis_timeseries_gapfinder.main() should be callable from everywhere
BASE_DIR = Path(__file__).parent.parent
assert BASE_DIR.name == "hdsr_fewspy", f"BASE_DIR must be hdsr_fewspy, but is {BASE_DIR.name}"

API_BASE_URL_TEST = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"
API_DOCUMENT_FORMAT = "PI_JSON"


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
