from datetime import datetime
from hdsr_fewspy.constants.paths import TEST_INPUT_DIR
from hdsr_fewspy.converters.xml_to_python_obj import parse
from pathlib import Path
from typing import Dict

import json
import pandas as pd


class RequestTimeSeriesBase:
    @classmethod
    def file_dir_expected_files(cls) -> Path:
        raise NotImplementedError

    @classmethod
    def get_expected_jsons(cls) -> Dict:
        dir_path = cls.file_dir_expected_files()
        assert dir_path.is_dir()

        file_paths = [x for x in dir_path.iterdir() if x.is_file() and x.suffix == ".json"]
        assert file_paths

        response_jsons = dict()
        for file_path in file_paths:
            with open(file_path.as_posix()) as src:
                response_json = json.load(src)
            response_jsons[file_path.stem] = response_json
        return response_jsons

    @classmethod
    def get_expected_xmls(cls) -> Dict:
        dir_path = cls.file_dir_expected_files()
        assert dir_path.is_dir()

        file_paths = [x for x in dir_path.iterdir() if x.is_file() and x.suffix == ".xml"]
        assert file_paths

        response_xmls = dict()
        for file_path in file_paths:
            response_xml = parse(file_path.as_posix())
            response_xmls[file_path.stem] = response_xml
        return response_xmls

    @classmethod
    def get_expected_dfs_from_csvs(cls) -> Dict:
        dir_path = cls.file_dir_expected_files()
        assert dir_path.is_dir()

        file_paths = [x for x in dir_path.iterdir() if x.is_file() and x.suffix == ".csv"]
        assert file_paths

        csv_paths = dict()
        for file_path in file_paths:
            df = pd.read_csv(filepath_or_buffer=file_path.as_posix(), sep=",")
            csv_paths[file_path.stem] = df
        return csv_paths


class RequestTimeSeriesSingleShort(RequestTimeSeriesBase):
    """Single as we use 1 location_ids and 1 parameter_ids."""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = "OW433001"
    parameter_ids = "H.G.0"
    start_time = datetime(2012, 1, 1)
    end_time = datetime(2012, 1, 2)

    @classmethod
    def file_dir_expected_files(cls) -> Path:
        return TEST_INPUT_DIR / "RequestTimeSeriesSingle1"


class RequestTimeSeriesSingleLong(RequestTimeSeriesBase):
    """Long timeseries"""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = "OW433001"
    parameter_ids = "H.G.0"
    start_time = datetime(2012, 1, 1)
    end_time = datetime(2016, 1, 1)

    @classmethod
    def file_dir_expected_files(cls) -> Path:
        return Path("not used in test")


class RequestTimeSeriesSingleNaN(RequestTimeSeriesBase):
    """Location does not exists"""

    location_ids = "OW1234"
    parameter_ids = "H.G.O"
    start_time = datetime(year=2022, month=11, day=1)
    end_time = datetime(year=2022, month=11, day=3)

    @classmethod
    def file_dir_expected_files(cls) -> Path:
        return Path("not used in test")


class RequestTimeSeriesMulti1(RequestTimeSeriesBase):
    """Multi since we use 2 location_ids."""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)

    location_ids = ["OW433001", "OW433002"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2012, 1, 1)
    end_time = datetime(2012, 1, 2)

    @classmethod
    def file_dir_expected_files(cls) -> Path:
        return TEST_INPUT_DIR / "RequestTimeSeriesMulti1"


class RequestTimeSeriesMulti2(RequestTimeSeriesBase):
    """Multi since we use 2 location_ids and 2 parameter_ids."""

    #     KW215710 (hoofdlocatie met gemaal)
    #     KW215712 (gemaal) pars:
    #       - wel Q.B.y (debiet wis jaar)   = 2006-12-31 tm 2022-12-31
    #       - wel DD.y (draaiduur jaar)     = 2005-12-31 tm 2022-12-31
    #     KW322613 (hoofdlocatie met gemaal)
    #     KW322613 (gemaal) met pars:
    #       - wel Q.B.y (debiet wis jaar)   = 2004-12-31 tm 2022-12-31
    #       - geen DD.y (draaiduur jaar)    = 2005-12-31 tm 2022-12-31

    location_ids = ["KW215712", "KW322613"]
    parameter_ids = ["Q.B.y", "DD.y"]
    start_time = datetime(2005, 1, 1)
    end_time = datetime(2005, 1, 2)

    @classmethod
    def file_dir_expected_files(cls) -> Path:
        return TEST_INPUT_DIR / "RequestTimeSeriesMulti2"
