from fewspy.api_calls.time_series.base import GetTimeSeriesBase
from fewspy.constants.choices import OutputChoices
from fewspy.constants.custom_types import ResponseType
from fewspy.converters.json_to_df_timeseries import response_jsons_to_one_df
from fewspy.utils.date_frequency import DateFrequencyBuilder
from typing import List
from typing import Union

import pandas as pd


class GetTimeSeriesSingle(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        assert isinstance(self.location_ids, str) and self.location_ids and "," not in self.location_ids
        assert isinstance(self.parameter_ids, str) and self.parameter_ids and "," not in self.parameter_ids
        if self.qualifier_ids:
            assert isinstance(self.qualifier_ids, str) and "," not in self.qualifier_ids

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def run(self) -> Union[List[ResponseType], pd.DataFrame]:
        date_ranges, date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
            startdate_obj=pd.Timestamp(self.start_time),
            enddate_obj=pd.Timestamp(self.end_time),
            frequency=self.request_settings.default_request_period,
        )
        responses = self._download_timeseries(
            date_ranges=date_ranges,
            date_range_freq=date_range_freq,
            request_params=self.initial_fews_parameters,
        )

        if self.output_choice in {OutputChoices.json_response_in_memory, OutputChoices.xml_response_in_memory}:
            return responses

        # parse the response to dataframe
        df = response_jsons_to_one_df(
            responses=responses, drop_missing_values=self.drop_missing_values, flag_threshold=self.flag_threshold
        )
        return df
