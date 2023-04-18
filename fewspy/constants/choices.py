from enum import Enum
from typing import List


class PiRestDocumentFormatChoices:
    xml = "PI_XML"
    json = "PI_JSON"

    @classmethod
    def get_all(cls) -> List[str]:
        return [cls.xml, cls.json]


class OutputChoices:
    xml_file_in_download_dir = "xml_file_in_download_dir"
    json_file_in_download_dir = "json_file_in_download_dir"
    csv_file_in_download_dir = "csv_file_in_download_dir"
    xml_response_in_memory = "xml_response_in_memory"
    json_response_in_memory = "json_response_in_memory"
    pandas_dataframe_in_memory = "pandas_dataframe_in_memory"

    @classmethod
    def get_pi_rest_document_format(cls, output_choice: str) -> str:
        if output_choice in {cls.xml_file_in_download_dir, cls.xml_response_in_memory}:
            return PiRestDocumentFormatChoices.xml
        return PiRestDocumentFormatChoices.json

    @classmethod
    def get_all(cls) -> List[str]:
        return [
            cls.xml_file_in_download_dir,
            cls.json_file_in_download_dir,
            cls.csv_file_in_download_dir,
            cls.xml_response_in_memory,
            cls.json_response_in_memory,
            cls.pandas_dataframe_in_memory,
        ]


class TimeZoneChoices(Enum):
    gmt = "GMT"  # "Etc/GMT" -> 0.0
    gmt_0 = "Etc/GMT-0"  # -> 0.0
    eu_amsterdam = "Europe/Amsterdam"  # -> 1.0

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]

    @classmethod
    def date_string_format(cls) -> str:
        return "%Y-%m-%dT%H:%M:%SZ"


class ApiParameters:

    attributes = "attributes"
    document_format = "document_format"
    document_version = "document_version"
    end_time = "end_time"
    filter_id = "filter_id"
    include_location_relations = "include_location_relations"
    location_ids = "location_ids"
    module_instance_ids = "module_instance_ids"
    omit_empty_timeseries = "omit_empty_timeSeries"
    only_headers = "only_headers"
    parameter_ids = "parameter_ids"
    qualifier_ids = "qualifier_ids"
    show_statistics = "show_statistics"
    start_time = "start_time"
    thinning = "thinning"

    @classmethod
    def pi_settings_keys(cls):
        return [cls.document_format, cls.document_version, cls.filter_id, cls.module_instance_ids]

    @classmethod
    def non_pi_settings_keys_datetime(cls):
        return [cls.start_time, cls.end_time]

    @classmethod
    def non_pi_settings_keys_non_datetime(cls):
        return [
            cls.attributes,
            cls.include_location_relations,
            cls.location_ids,
            cls.omit_empty_timeseries,
            cls.only_headers,
            cls.parameter_ids,
            cls.qualifier_ids,
            cls.show_statistics,
            cls.thinning,
        ]

    @classmethod
    def non_pi_settings_keys(cls):
        return cls.non_pi_settings_keys_non_datetime() + cls.non_pi_settings_keys_datetime()
