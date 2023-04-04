from fewspy.constants.choices import ApiParameters
from fewspy.constants.pi_settings import PiSettings
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.conversions import snake_to_camel_case
from typing import Any
from typing import Tuple


def parameters_to_fews(parameters: dict, pi_settings: PiSettings) -> dict:
    """Prepare Python API dictionary for FEWS API request."""

    def _convert_kv(k: str, v) -> Tuple[str, Any]:
        if k in ApiParameters.non_pi_settings_keys_datetime():
            v = datetime_to_fews_str(v)
        elif k == "attributes":
            k = "show_attributes"
            v = True
        k = snake_to_camel_case(k)
        return k, v

    params_non_pi = [_convert_kv(k, v) for k, v in parameters.items() if k in ApiParameters.non_pi_settings_keys()]
    params_pi = [_convert_kv(k, v) for k, v in pi_settings.all_fields.items() if k in ApiParameters.pi_settings_keys()]
    fews_parameters = {x[0]: x[1] for x in params_non_pi + params_pi if x[1] is not None}
    return fews_parameters
