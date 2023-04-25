from fewspy.api_calls.time_series.get_time_series_single import GetTimeSeriesSingle
from fewspy.constants.choices import OutputChoices
from fewspy.constants.custom_types import ResponseType
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetTimeSeriesStatistics(GetTimeSeriesSingle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
        ]

    def run(self) -> ResponseType:
        return self._get_statistics(request_params=self.filtered_fews_parameters)
