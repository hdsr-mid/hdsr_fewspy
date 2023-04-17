from fewspy.constants.choices import OutputChoices
from pathlib import Path
from typing import List
import json
import logging
import requests


logger = logging.getLogger(__name__)


class Base:
    def __init__(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError


class DownloadBase(Base):
    def __init__(self, request_method: str, output_directory_root: Path):
        self.request_method = request_method
        self.output_directory_root = output_directory_root
        super().__init__()

    def run(self, responses: List[requests.models.Response], file_name_values: List[str]):
        raise NotImplementedError

    @classmethod
    def _normalize_string(cls, value: str) -> str:
        value = value.lower()
        for char in [".", ",", "-", "_", ":"]:
            value = value.replace(char, "")
        return value

    def _get_file_name(self, file_name_values: List[str]):
        """Every download file must have a name with some values in it to distinguish the request."""
        nr_values = len(file_name_values)
        assert 2 < nr_values < 6, "nr_values must be between 2 and 6 otherwise filename to short or long"
        file_name = self.request_method
        for file_name_value in file_name_values:
            file_name_value_new = self._normalize_string(value=file_name_value)
            file_name += f"_{file_name_value_new}"
        return file_name


class MemoryBase(Base):
    def __init__(self):
        super().__init__()

    def run(self, responses: List[requests.models.Response]):
        raise NotImplementedError


class XmlDownloadDir(DownloadBase):
    def run(self, responses: List[requests.models.Response], file_name_values: List[str]):
        print(1)


class JsonDownloadDir(DownloadBase):
    def run(self, responses: List[requests.models.Response], file_name_values: List[str]) -> List[Path]:
        file_paths_created = []
        for index, response in enumerate(responses):
            file_name = self._get_file_name(file_name_values=file_name_values)
            file_path = self.output_directory_root / f"{file_name}_{index}.json"
            logger.info(f"writing response to new file {file_path}")
            with open(file=file_path.as_posix(), mode="w", encoding="utf-8") as json_file:
                # indent=None results in half the file size compared to indent=4
                json.dump(obj=response.json(), fp=json_file, ensure_ascii=False, indent=None)
            file_paths_created.append(file_path)
        return file_paths_created


class CsvDownloadDir(DownloadBase):
    def run(self, responses: List[requests.models.Response], file_name_values: List[str]):
        print(1)


class XmlMemory(MemoryBase):
    def run(self, responses: List[requests.models.Response]):
        print(1)


class JsonMemory(MemoryBase):
    def run(self, responses: List[requests.models.Response]):
        print(1)


class PdDataFrameMemory(MemoryBase):
    def run(self, responses: List[requests.models.Response]):
        print(1)


class ResponseManager:
    """Uses a specific response_handler based on output_choice."""

    def __init__(self, output_choice: str, request_method: str, output_directory_root: Path = None):
        self.output_choice = output_choice
        self.request_method = request_method
        self.output_directory_root = output_directory_root
        self.response_handler = self._get_response_handler()

    def _get_response_handler(self):
        mapper = {
            OutputChoices.xml_file_in_download_dir: XmlDownloadDir(
                request_method=self.request_method, output_directory_root=self.output_directory_root
            ),
            OutputChoices.json_file_in_download_dir: JsonDownloadDir(
                request_method=self.request_method, output_directory_root=self.output_directory_root
            ),
            OutputChoices.csv_file_in_download_dir: CsvDownloadDir(
                request_method=self.request_method, output_directory_root=self.output_directory_root
            ),
            OutputChoices.xml_response_in_memory: XmlMemory(),
            OutputChoices.json_response_in_memory: JsonMemory(),
            OutputChoices.pandas_dataframe_in_memory: PdDataFrameMemory(),
        }
        response_handler = mapper.get(self.output_choice, None)
        if not response_handler:
            raise AssertionError(f"code error: output_choice {self.output_choice} must be in {mapper.keys()}")

        return response_handler

    def run(self, responses: List[requests.models.Response], file_name_values: List[str] = None):
        if file_name_values:
            return self.response_handler.run(responses=responses, file_name_values=file_name_values)
        return self.response_handler.run(responses=responses)
