from fewspy.api_calls.time_series.base import GetTimeSeriesBase
from fewspy.constants.choices import OutputChoices
from typing import List


class GetTimeSeriesSingle(GetTimeSeriesBase):
    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.json_response_in_memory,
            OutputChoices.xml_response_in_memory,
            OutputChoices.pandas_dataframe_in_memory,
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        pass

    def run(self):
        pass
