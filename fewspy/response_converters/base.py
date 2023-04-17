from datetime import datetime
from fewspy.constants.choices import OutputChoices
from pathlib import Path
from typing import Dict


class Base:
    def __init__(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError


class DownloadBase(Base):
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        super().__init__()

    def run(self, response, file_name_params):
        raise NotImplementedError

    @classmethod
    def _normalize_string(cls, value: str) -> str:
        value = value.lower()
        for char in [".", ",", "-", ":"]:
            value = value.replace(char, "")
        return value

    def _get_file_name(self, parameters: Dict, extension: str):
        """Every download file must have a name with some parameters in it to distinguish the request."""
        assert extension in (".csv", ".xml", ".json")
        nr_parameters = len(parameters.keys())
        assert 2 < nr_parameters < 6, f"nr_parameters must be between 2 and 6 otherwise filename to short or long"
        file_name_parts = []
        for key, value in parameters.items():
            if not value:
                continue
            key_new = self._normalize_string(value=key)
            value_new = self._normalize_string(value=value)
            file_name_parts.append(f"{key_new}_{value_new}")
        file_name = file_name_parts[0]
        for file_name_part in file_name_parts[1:]:
            file_name = f"{file_name}__{file_name_part}"
        return file_name

    def save_response_to_file(self, response):
        raise AssertionError
        # assert self.output_directory
        # datetime_filename = datetime.now().strftime("%Y%m%d_%H%M%S")
        # file_path = self.output_directory / datetime_filename
        # with open(file=file_path.as_posix(), mode="wb") as file:
        #     file.write(response.content)
        #
        #     with open("out.xls", "wb") as file:
        #         file.write(response.content)
        #     import json
        #
        #     response.json()
        #     with open("data.json", "w", encoding="utf-8") as f:
        #         json.dump(data, f, ensure_ascii=False, indent=4)


class MemoryBase(Base):
    def __init__(self):
        super().__init__()

    def run(self, response):
        raise NotImplementedError


class XmlDownloadDir(DownloadBase):
    def run(self, response, file_name_params):
        print(1)


class JsonDownloadDir(DownloadBase):
    def run(self, response, file_name_params):
        print(1)


class CsvDownloadDir(DownloadBase):
    def run(self, response, file_name_params):
        print(1)


class XmlMemory(MemoryBase):
    def run(self, response):
        print(1)


class JsonMemory(MemoryBase):
    def run(self, response):
        print(1)


class PdDataFrameMemory(MemoryBase):
    def run(self, response):
        print(1)


class ResponseManager:
    """Uses a specific response_handler based on output_choice."""

    def __init__(self, output_choice: str, output_directory_root: Path = None):
        self.output_choice = output_choice
        self.output_directory_root = output_directory_root
        self.response_handler = self._get_response_handler()

    def _get_response_handler(self):
        mapper = {
            OutputChoices.xml_file_in_download_dir: XmlDownloadDir(output_directory=self.output_directory_root),
            OutputChoices.json_file_in_download_dir: JsonDownloadDir(output_directory=self.output_directory_root),
            OutputChoices.csv_file_in_download_dir: CsvDownloadDir(output_directory=self.output_directory_root),
            OutputChoices.xml_response_in_memory: XmlMemory(),
            OutputChoices.json_response_in_memory: JsonMemory(),
            OutputChoices.pandas_dataframe_in_memory: PdDataFrameMemory(),
        }
        response_handler = mapper.get(self.output_choice, None)
        if not response_handler:
            raise AssertionError(f"code error: output_choice {self.output_choice} must be in {mapper.keys()}")

        return response_handler

    def handle_response(self, response, file_name_params: Dict = None):
        return self.response_handler.run(response, file_name_params)
