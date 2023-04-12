from fewspy.api_calls.time_series.base import GetTimeSeriesBase
from fewspy.constants.choices import PiRestDocumentFormatChoices


class GetTimeSeriesSingle(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        pass

    def run(self):
        pass
