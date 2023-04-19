from fewspy.constants.choices import OutputChoices
from fewspy.constants.custom_types import ResponseType
from fewspy.response_converters.download import CsvDownloadDir
from fewspy.response_converters.download import JsonDownloadDir
from fewspy.response_converters.download import XmlDownloadDir
from fewspy.response_converters.memory import JsonMemory
from fewspy.response_converters.memory import PdDataFrameMemory
from fewspy.response_converters.memory import XmlMemory
from pathlib import Path
from typing import List


class ResponseManager:
    """Relates a output_choice to the related Response Handler."""

    def __init__(self, output_choice: str, request_class: str, output_dir: Path = None):
        self.output_choice = output_choice
        self.request_class = request_class  # e.g. gettimeseriesmulti
        self.output_dir = output_dir
        self.response_handler = self._get_response_handler()

    def _get_response_handler(self):
        OutputChoices.validate(output_choice=self.output_choice)
        if self.output_choice == OutputChoices.xml_file_in_download_dir:
            return XmlDownloadDir(request_class=self.request_class, output_dir=self.output_dir)
        elif self.output_choice == OutputChoices.json_file_in_download_dir:
            return JsonDownloadDir(request_class=self.request_class, output_dir=self.output_dir)
        elif self.output_choice == OutputChoices.csv_file_in_download_dir:
            return CsvDownloadDir(request_class=self.request_class, output_dir=self.output_dir)
        elif self.output_choice == OutputChoices.xml_response_in_memory:
            return XmlMemory()
        elif self.output_choice == OutputChoices.json_response_in_memory:
            return JsonMemory()
        elif self.output_choice == OutputChoices.pandas_dataframe_in_memory:
            return PdDataFrameMemory()

    def run(self, responses: List[ResponseType], **kwargs):
        # allowed_kwargs = ["file_name_values", "drop_missing_values", "flag_threshold"]
        return self.response_handler.run(responses=responses, **kwargs)
