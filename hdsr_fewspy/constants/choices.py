from __future__ import annotations

from enum import Enum
from typing import List
from typing import Union


class ChoicesBase(Enum):
    @classmethod
    def get_all_values(cls):
        return [x.value for x in cls.__members__.values()]

    @classmethod
    def is_member_value(cls, value: str):
        return value in cls.get_all_values()


class PiRestDocumentFormatChoices(ChoicesBase):
    xml = "PI_XML"
    json = "PI_JSON"


class TimeSeriesDateTimeKeys(ChoicesBase):
    start_date = "start_date"
    end_date = "end_date"


class TimeSeriesFloatKeys(ChoicesBase):
    miss_val = "miss_val"
    lat = "lat"
    lon = "lon"
    x = "x"
    y = "y"
    z = "z"


class TimeSeriesEventColumns(ChoicesBase):
    datetime = "datetime"
    value = "value"
    flag = "flag"


class DefaultPiSettingsChoices(Enum):
    """
    Choices that must be present in https://github.com/hdsr-mid/hdsr_fewspy_auth/blob/main/settings.csv.

    Each choice has a different module_instance_id. We specify module_instance_id in settings.csv, to avoid
    requesting 3 time-series for one location. The module_instance_id's are:
     - ImportOpvlWater = raw data
     - WerkFilter = this data is being validated by HDSR person (data validator CAW). This data might change every day
     - MetingenFilter = validated data reeksen. This data is months behind the current situation.
    """

    efcis_production_point_fysische_chemie = "efcis_production_point_fysische_chemie"
    efcis_production_point_biologie = "efcis_production_point_biologie"

    wis_production_point_raw = "wis_production_point_raw"
    wis_production_point_work = "wis_production_point_work"
    wis_production_point_validated = "wis_production_point_validated"
    #
    wis_production_area_soilmoisture = "wis_production_area_soilmoisture"
    # module_instance_id=ImportBodemvocht,
    # parameter= e.g. SM.d
    # qualifiers=Lband05cm, Lband10cm, Lband20cm
    # noqa filterId=INTERNAL-API.GEBGEM&locationIds=AFVG13&parameterIds=SM.d&moduleInstanceIds=ImportBodemvocht&startTime=2020-01-01T00%3A00%3A00Z&endTime=2023-01-01T00%3A00%3A00Z&onlyHeaders=true&showStatistics=true
    #
    wis_production_area_precipitation_wiwb = "wis_production_area_precipitation_wiwb"
    # module_instance_id ImportGridHistWiwb tm 2019
    # parameter = e.g. Rh.h
    # qualifiers=wiwb_merge
    # noqa filterId=INTERNAL-API.GEBGEM&locationIds=AFVG13&parameterIds=Rh.h&moduleInstanceIds=ImportGridHistWiwb&startTime=2015-01-01T00%3A00%3A00Z&endTime=2023-01-01T00%3A00%3A00Z&onlyHeaders=true&showStatistics=true
    #
    wis_production_area_precipitation_radarcorrection = "wis_production_area_precipitation_radarcorrection"
    # module_instance_id RadarCorrectie vanaf 2019
    # parameter = e.g. Rh.h
    # qualifiers=mfbs_merge
    # noqa filterId=INTERNAL-API.GEBGEM&locationIds=AFVG13&parameterIds=Rh.h&moduleInstanceIds=RadarCorrectie&startTime=2015-01-01T00%3A00%3A00Z&endTime=2023-01-01T00%3A00%3A00Z&onlyHeaders=true&showStatistics=true

    wis_production_area_evaporation_wiwb_satdata = "wis_production_area_evaporation_wiwb_satdata"
    # module_instance_id=ImportWiwbSatData
    # parameter= e.g. Eact.d
    # qualifiers=satdata_merge, RA, None
    # noqa filterId=INTERNAL-API.GEBGEM&locationIds=AFVG13&parameterIds=Eact.d&moduleInstanceIds=ImportWiwbSatData&startTime=2015-01-01T00%3A00%3A00Z&endTime=2023-01-01T00%3A00%3A00Z&onlyHeaders=true&showStatistics=true

    wis_production_area_evaporation_waterwatch = "wis_production_area_evaporation_waterwatch"
    # module_instance_id=ImportWaterwatch
    # parameter= e.g. Eact.d
    # qualifiers=None
    # noqa filterId=INTERNAL-API.GEBGEM&locationIds=AFVG13&parameterIds=Eact.d&moduleInstanceIds=ImportWaterwatch&startTime=2020-01-01T00%3A00%3A00Z&endTime=2023-01-01T00%3A00%3A00Z

    wis_stand_alone_point_raw = "wis_stand_alone_point_raw"
    wis_stand_alone_point_work = "wis_stand_alone_point_work"
    wis_stand_alone_point_validated = "wis_stand_alone_point_validated"

    @classmethod
    def get_all(cls) -> List[DefaultPiSettingsChoices]:
        return [x for x in cls.__members__.values()]

    @property
    def is_fews_efcis(self):
        return self in {self.efcis_production_point_fysische_chemie, self.efcis_production_point_biologie}

    def is_fews_wis(self):
        return not self.is_fews_efcis


class OutputChoices(Enum):
    xml_file_in_download_dir = "xml_file_in_download_dir"
    json_file_in_download_dir = "json_file_in_download_dir"
    csv_file_in_download_dir = "csv_file_in_download_dir"
    xml_response_in_memory = "xml_response_in_memory"
    json_response_in_memory = "json_response_in_memory"
    pandas_dataframe_in_memory = "pandas_dataframe_in_memory"

    @classmethod
    def validate(cls, output_choice: OutputChoices) -> OutputChoices:
        assert isinstance(output_choice, OutputChoices)
        return output_choice

    @classmethod
    def get_pi_rest_document_format(cls, output_choice: OutputChoices) -> PiRestDocumentFormatChoices:
        output_choice = cls.validate(output_choice=output_choice)
        if output_choice in [cls.xml_file_in_download_dir, cls.xml_response_in_memory]:
            return PiRestDocumentFormatChoices.xml
        return PiRestDocumentFormatChoices.json

    @classmethod
    def needs_output_dir(cls, output_choice: OutputChoices) -> bool:
        cls.validate(output_choice=output_choice)
        return output_choice in {
            cls.xml_file_in_download_dir,
            cls.json_file_in_download_dir,
            cls.csv_file_in_download_dir,
        }

    @classmethod
    def get_all(cls) -> List[OutputChoices]:
        return [x for x in cls.__members__.values()]


class TimeZoneChoices(Enum):
    gmt = 0.0  # ["GMT"= "Etc/GMT" = "Etc/GMT-0"]
    eu_amsterdam = 1.0  # ["Europe/Amsterdam"]

    @classmethod
    def get_hdsr_default(cls):
        return cls.gmt

    @classmethod
    def get_all(cls) -> List[TimeZoneChoices]:
        return [x for x in cls.__members__.values()]

    @classmethod
    def get_all_values(cls) -> List[float]:
        return [x.value for x in cls.__members__.values()]

    @classmethod
    def date_string_format(cls) -> str:
        return "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def get_tz_float(cls, value: Union[str, float, int]) -> float:
        mapper = {
            "GMT": cls.gmt.value,
            "GMT-0": cls.gmt.value,
            "Etc/GMT": cls.gmt.value,
            "Etc/GMT-0": cls.gmt.value,
            "Europe/Amsterdam": cls.eu_amsterdam.value,
        }
        if isinstance(value, str):
            if value in mapper.keys():
                return mapper[value]
        msg = "could not determine time-zone float (0.0, 1.0, etc) for"
        try:
            float_value = float(value)
        except ValueError:
            raise AssertionError(f"{msg} value '{value}'")
        assert float_value in cls.get_all_values(), f"{msg} value '{value}' and float_value '{float_value}'"
        return float_value


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
    omit_empty_time_series = "omit_empty_timeSeries"
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
            cls.omit_empty_time_series,
            cls.only_headers,
            cls.parameter_ids,
            cls.qualifier_ids,
            cls.sample_ids,
            cls.show_attributes,
            cls.show_statistics,
            cls.thinning,
        ]
