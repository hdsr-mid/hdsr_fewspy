from fewspy.wrappers.get_filters import get_filters
from fewspy.wrappers.get_locations import get_locations
from fewspy.wrappers.get_parameters import get_parameters
from fewspy.wrappers.get_qualifiers import GetQualifiers
from fewspy.wrappers.get_samples import get_samples
from fewspy.wrappers.get_time_series import GetTimeseries
from fewspy.wrappers.get_timezone_id import get_timezone_id


# silence flake8 errors
get_filters = get_filters
get_locations = get_locations
get_parameters = get_parameters
get_qualifiers = GetQualifiers.get_qualifiers
get_samples = get_samples
get_time_series = GetTimeseries.get_time_series
get_timezone_id = get_timezone_id
