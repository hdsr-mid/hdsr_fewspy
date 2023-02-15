from fewspy.constants import ApiKeys
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.conversions import snake_to_camel_case
from typing import Any
from typing import Tuple


api_keys_datetime = [ApiKeys.start_time, ApiKeys.end_time]
api_keys_non_datetime = [
    ApiKeys.document_format,
    ApiKeys.document_version,
    ApiKeys.end_time,
    ApiKeys.filter_id,
    ApiKeys.include_location_relations,
    ApiKeys.location_ids,
    ApiKeys.only_headers,
    ApiKeys.parameter_ids,
    ApiKeys.qualifier_ids,
    ApiKeys.attributes,
    ApiKeys.show_statistics,
    ApiKeys.start_time,
    ApiKeys.thinning,
]
all_keys = api_keys_datetime + api_keys_non_datetime


def parameters_to_fews(parameters: dict) -> dict:
    """Prepare Python API dictionary for FEWS API request."""

    def _convert_kv(k: str, v) -> Tuple[str, Any]:
        if k in api_keys_datetime:
            v = datetime_to_fews_str(v)
        elif k == "attributes":
            k = "show_attributes"
            v = True
        k = snake_to_camel_case(k)
        return k, v

    args = (_convert_kv(k, v) for k, v in parameters.items() if k in all_keys)
    args = (i for i in args if i[1] is not None)
    fews_parameters = {i[0]: i[1] for i in args}
    return fews_parameters
