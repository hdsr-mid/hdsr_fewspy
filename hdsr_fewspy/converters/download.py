from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.converters.json_to_df_timeseries import response_jsons_to_one_df
from pathlib import Path
from typing import Dict
from typing import List

import json
import logging
import requests
import xml.etree.cElementTree as ET  # TODO: from xml.etree import ElementTree


logger = logging.getLogger(__name__)


class DownloadBase:
    def __init__(self, request_class: str, output_dir: Path):
        self.request_class = request_class
        self.output_dir = self._validate_output_dir(output_dir)
        super().__init__()

    @staticmethod
    def _validate_output_dir(output_dir: Path) -> Path:
        assert output_dir, "if you want to download a output_dir is required. Please specify Api output_directory_root"
        assert isinstance(output_dir, Path), f"code error: output_dir {output_dir} must be Path (conversion in Api)"
        return output_dir

    @staticmethod
    def _get_base_file_name(request_class: str, file_name_values: List[str]) -> str:
        """Every download file must have a name with some values in it to distinguish the request.

        Example:
            request_class = gettimeseriesmulti
            file_name_values - ['OW433001', 'H.G.0', None, '2012-01-01T00:00:00Z', '2012-01-02T00:00:00Z']

            returns 'gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z'
        """
        file_name_values = [x for x in file_name_values if x]
        # TODO: add example base_file_name to docstring
        nr_values = len(file_name_values)
        if not (2 < nr_values < 6):
            msg = f"nr file_name_values {file_name_values} must be between 2 and 6, otherwise filename to short or long"
            raise AssertionError(msg)

        def _get_normalize_string(value: str) -> str:
            value = value.lower()
            for char in [" ", ".", ",", "-", "_", ":"]:
                value = value.replace(char, "")
            return value

        base_file_name = request_class
        for file_name_value in file_name_values:
            normalize_string = _get_normalize_string(value=file_name_value)
            base_file_name = f"{base_file_name}_{normalize_string}"
        return base_file_name

    def _ensure_output_dir_exists(self, file_path: Path) -> None:
        if file_path.parent != self.output_dir:
            raise AssertionError(f"file_path {file_path} cannot be saved in output_dir {self.output_dir}")
        if not self.output_dir.is_dir():
            logger.info(f"create output_dir {self.output_dir}")
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, responses: List[requests.models.Response], file_name_values: List[str], **kwargs):
        raise NotImplementedError


class XmlDownloadDir(DownloadBase):
    @staticmethod
    def create_custom_xml_tree(data: Dict):
        root = ET.Element("root")
        doc = ET.SubElement(root, "doc")
        for key, value in data.items():
            ET.SubElement(doc, key, name=key).text = str(value)
        tree = ET.ElementTree(root)
        return tree

    def run(self, responses: List[ResponseType], file_name_values: List[str], **kwargs) -> List[Path]:
        """Create for every response a separate .xml file.
        All responses are for a unique location_parameter_qualifier combi in get_time_series_multi."""
        file_name_base = self._get_base_file_name(request_class=self.request_class, file_name_values=file_name_values)
        file_paths_created = []
        for index, response in enumerate(responses):
            file_path = self.output_dir / f"{file_name_base}_{index}.xml"
            logger.info(f"writing response to new file {file_path}")
            self._ensure_output_dir_exists(file_path=file_path)
            if response.status_code != 200:
                response_in_xml = self.create_custom_xml_tree(
                    data={"response_http_status": response.status_code, "response_text": response.text}
                )
                response_in_xml.write(file_or_filename=file_path.as_posix(), encoding="utf-8")
            else:
                with open(file=file_path.as_posix(), mode="w", encoding="utf-8") as xml_file:
                    xml_file.write(response.text)
            file_paths_created.append(file_path)
        return file_paths_created


class JsonDownloadDir(DownloadBase):
    def run(self, responses: List[ResponseType], file_name_values: List[str], **kwargs) -> List[Path]:
        """Create for every response a separate .json file.
        All responses are for a unique location_parameter_qualifier combi in get_time_series_multi."""
        file_name_base = self._get_base_file_name(request_class=self.request_class, file_name_values=file_name_values)
        file_paths_created = []
        for index, response in enumerate(responses):
            file_path = self.output_dir / f"{file_name_base}_{index}.json"
            logger.info(f"writing response to new file {file_path}")
            self._ensure_output_dir_exists(file_path=file_path)
            with open(file=file_path.as_posix(), mode="w", encoding="utf-8") as json_file:
                # indent=None results in half the file size compared to indent=4
                json.dump(obj=response.json(), fp=json_file, ensure_ascii=False, indent=None)
            file_paths_created.append(file_path)
        return file_paths_created


class CsvDownloadDir(DownloadBase):
    def run(self, responses: List[ResponseType], file_name_values: List[str], **kwargs) -> List[Path]:
        """Only for timeseries: Aggregate all responses into 1 .csv file as all responses are for a unique
        location_parameter_qualifier combi in get_time_series_multi."""
        drop_missing_values: bool = kwargs["drop_missing_values"]
        flag_threshold: int = kwargs["flag_threshold"]
        file_name_base = self._get_base_file_name(request_class=self.request_class, file_name_values=file_name_values)
        df = response_jsons_to_one_df(
            responses=responses, drop_missing_values=drop_missing_values, flag_threshold=flag_threshold
        )
        if df.empty:
            return []
        file_path = self.output_dir / f"{file_name_base}.csv"
        logger.info(f"writing response to new file {file_path}")
        self._ensure_output_dir_exists(file_path=file_path)
        df.to_csv(path_or_buf=file_path.as_posix(), sep=",", encoding="utf-8")
        return [file_path]