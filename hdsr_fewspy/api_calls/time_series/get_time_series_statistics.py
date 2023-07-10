from hdsr_fewspy.api_calls.time_series.get_time_series_single import GetTimeSeriesSingle
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from typing import List

import logging


logger = logging.getLogger(__name__)


class GetTimeSeriesStatistics(GetTimeSeriesSingle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        assert isinstance(self.location_ids, str) and self.location_ids and "," not in self.location_ids
        assert isinstance(self.parameter_ids, str) and self.parameter_ids and "," not in self.parameter_ids
        if self.qualifier_ids:
            assert isinstance(self.qualifier_ids, str) and "," not in self.qualifier_ids

        logger.warning(f"flag_threshold is not used for output_choice {self.output_choice}")
        if self.drop_missing_values == True:  # noqa
            logger.warning(f"drop_missing_values is not used for output_choice {self.output_choice}")

    @property
    def allowed_output_choices(self) -> List[OutputChoices]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
        ]

    def run(self) -> ResponseType:
        return self._get_statistics(request_params=self.filtered_fews_parameters)
