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
    def validate(cls, output_choice: str) -> str:
        assert output_choice in cls.get_all(), f"output_choice {output_choice} must be in {cls.get_all()}"
        return output_choice

    @classmethod
    def get_pi_rest_document_format(cls, output_choice: str) -> str:
        output_choice = cls.validate(output_choice=output_choice)
        if output_choice in {cls.xml_file_in_download_dir, cls.xml_response_in_memory}:
            return PiRestDocumentFormatChoices.xml
        return PiRestDocumentFormatChoices.json

    @classmethod
    def needs_output_dir(cls, output_choice: str) -> bool:
        cls.validate(output_choice=output_choice)
        return output_choice in {
            cls.xml_file_in_download_dir,
            cls.json_file_in_download_dir,
            cls.csv_file_in_download_dir,
        }

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


class TimeZoneChoices:
    gmt = "GMT"  # "Etc/GMT" -> 0.0
    gmt_0 = "Etc/GMT-0"  # -> 0.0
    eu_amsterdam = "Europe/Amsterdam"  # -> 1.0

    @classmethod
    def get_all(cls) -> List[str]:
        return [cls.gmt, cls.gmt_0, cls.eu_amsterdam]

    @classmethod
    def date_string_format(cls) -> str:
        return "%Y-%m-%dT%H:%M:%SZ"


class ApiParameters:

    document_format = "document_format"
    document_version = "document_version"
    end_creation_time = "end_creation_time"
    end_time = "end_time"
    filter_id = "filter_id"
    include_location_relations = "include_location_relations"
    location_ids = "location_ids"
    module_instance_ids = "module_instance_ids"
    omit_missing = "omit_missing"
    omit_empty_timeseries = "omit_empty_timeSeries"
    only_headers = "only_headers"
    parameter_ids = "parameter_ids"
    qualifier_ids = "qualifier_ids"
    sample_ids = "sample_ids"
    show_attributes = "show_attributes"
    show_statistics = "show_statistics"
    start_creation_time = "start_creation_time"
    start_time = "start_time"
    thinning = "thinning"

    @classmethod
    def pi_settings_keys(cls) -> List[str]:
        return [cls.document_format, cls.document_version, cls.filter_id, cls.module_instance_ids]

    @classmethod
    def non_pi_settings_keys(cls) -> List[str]:
        return cls.non_pi_settings_keys_non_datetime() + cls.non_pi_settings_keys_datetime()

    @classmethod
    def non_pi_settings_keys_datetime(cls) -> List[str]:
        return [cls.end_creation_time, cls.end_time, cls.start_creation_time, cls.start_time]

    @classmethod
    def non_pi_settings_keys_non_datetime(cls) -> List[str]:
        return [
            cls.include_location_relations,
            cls.location_ids,
            cls.omit_missing,
            cls.omit_empty_timeseries,
            cls.only_headers,
            cls.parameter_ids,
            cls.qualifier_ids,
            cls.sample_ids,
            cls.show_attributes,
            cls.show_statistics,
            cls.thinning,
        ]
