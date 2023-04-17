from datetime import datetime
from fewspy.constants.paths import TEST_INPUT_DIR
from pathlib import Path
from typing import Optional

import json


class SingleBase:
    @classmethod
    def file_path_expected_json(cls) -> Optional[Path]:
        raise NotImplementedError

    @classmethod
    def file_path_expected_xml(cls) -> Optional[Path]:
        raise NotImplementedError

    @classmethod
    def get_expected_json(cls):
        file_path = cls.file_path_expected_json()
        assert file_path.is_file()
        with open(file_path.as_posix()) as src:
            response_json = json.load(src)
        return response_json

    @classmethod
    def get_expected_xml(cls):
        file_path = cls.file_path_expected_xml()
        assert file_path.is_file()
        with open(file_path.as_posix()) as src:
            response_json = json.load(src)
        return response_json


class MultiBase:
    @classmethod
    def file_dir_expected_jsons(cls) -> Optional[Path]:
        raise NotImplementedError

    @classmethod
    def file_dir_expected_xmls(cls) -> Optional[Path]:
        raise NotImplementedError

    @classmethod
    def get_expected_jsons(cls):
        dir_path = cls.file_dir_expected_jsons()
        assert dir_path.is_dir()

        file_paths = [x for x in dir_path.iterdir() if x.is_file() and x.suffix == ".json"]
        assert file_paths

        response_jsons = []
        for file_path in file_paths:
            with open(file_path.as_posix()) as src:
                response_json = json.load(src)
            response_jsons.append(response_json)
        return response_jsons

    @classmethod
    def get_expected_xmls(cls):
        dir_path = cls.file_dir_expected_xmls()
        assert dir_path.is_dir()

        file_paths = [x for x in dir_path.iterdir() if x.is_file() and x.suffix == ".xml"]
        assert file_paths

        response_xmls = []
        for file_path in file_paths:
            with open(file_path.as_posix()) as src:
                raise NotImplementedError
                response_xml = json.load(src)
            response_xmls.append(response_xml)
        return response_xmls


class RequestTimeSeriesSingle1(SingleBase):
    """Single as we use 1 location_ids and 1 parameter_ids."""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = ["OW433001"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2012, 1, 1)
    end_time = datetime(2012, 1, 2)

    @classmethod
    def file_path_expected_json(cls):
        return TEST_INPUT_DIR / "RequestTimeSeriesSingle1.json"

    @classmethod
    def file_path_expected_xml(cls):
        raise NotImplementedError


class RequestTimeSeriesMulti1(MultiBase):
    """Multi since we use 2 location_ids."""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    # TODO
    location_ids = ["OW433001", "OW433002"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2012, 1, 1)
    end_time = datetime(2012, 1, 3)

    @classmethod
    def file_dir_expected_jsons(cls) -> Optional[Path]:
        pass

    @classmethod
    def file_dir_expected_xmls(cls):
        raise NotImplementedError


class RequestTimeSeriesMulti2(MultiBase):
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
    end_time = datetime(2023, 1, 1)

    @classmethod
    def file_dir_expected_jsons(cls) -> Optional[Path]:
        pass

    @classmethod
    def file_dir_expected_xmls(cls):
        raise NotImplementedError
