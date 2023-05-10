from hdsr_fewspy.api_calls.time_series.base import GetTimeSeriesBase
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.converters.json_to_df_timeseries import response_jsons_to_one_df
from hdsr_fewspy.date_frequency import DateFrequencyBuilder
from typing import List
from typing import Union

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesSingle(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        assert isinstance(self.location_ids, str) and self.location_ids and "," not in self.location_ids
        assert isinstance(self.parameter_ids, str) and self.parameter_ids and "," not in self.parameter_ids
        if self.qualifier_ids:
            assert isinstance(self.qualifier_ids, str) and "," not in self.qualifier_ids

        if self.output_choice != OutputChoices.pandas_dataframe_in_memory:
            logger.warning(f"flag_threshold is not used for output_choice {self.output_choice}")
            if self.drop_missing_values == True:  # noqa
                logger.warning(f"drop_missing_values is not used for output_choice {self.output_choice}")

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self) -> Union[List[ResponseType], pd.DataFrame]:
        # eventually continue with request_period of last request (avoiding all freq update iterations)
        frequency = (
            self.request_settings.updated_request_period
            if self.request_settings.updated_request_period
            else self.request_settings.default_request_period
        )
        date_ranges, date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
            startdate_obj=pd.Timestamp(self.start_time), enddate_obj=pd.Timestamp(self.end_time), frequency=frequency
        )
        responses = self._download_timeseries(
            date_ranges=date_ranges,
            date_range_freq=date_range_freq,
            request_params=self.initial_fews_parameters,
        )

        if self.output_choice in {OutputChoices.json_response_in_memory, OutputChoices.xml_response_in_memory}:
            return responses

        assert self.output_choice == OutputChoices.pandas_dataframe_in_memory, "code error GetTimeSeriesSingle"
        # parse the response to dataframe
        df = response_jsons_to_one_df(
            responses=responses, drop_missing_values=self.drop_missing_values, flag_threshold=self.flag_threshold
        )
        return df
