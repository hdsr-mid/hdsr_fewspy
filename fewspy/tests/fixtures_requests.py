from datetime import datetime
from fewspy.constants.paths import BASE_DIR

import json


class RequestData1:
    """get_timeseries()."""

    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    location_ids = ["OW433001"]
    parameter_ids = ["H.G.0"]
    start_time = datetime(2022, 5, 1)
    end_time = datetime(2022, 5, 2)

    @classmethod
    def get_expected_json(cls):
        file_path = BASE_DIR / "fewspy" / "tests" / "data" / "input" / "expected_json.json"
        assert file_path.is_file()
        with open(file_path.as_posix()) as src:
            response_json = json.load(src)
        return response_json


class RequestData2:
    """
    get_timeseries().

    KW215710 (hoofdlocatie met gemaal)
    KW215712 (gemaal) pars:
      - wel Q.B.y (debiet wis jaar) = begin 2007 tm eind 2022
      - wel DD.y (draaiduur jaar) = begin 2006 tm eind 2022
    KW322613 (hoofdlocatie met gemaal)
    KW322613 (gemaal) met pars:
      - wel Q.B.y (debiet wis jaar) = begin 2004 tm eind 2022
      - geen DD.y (draaiduur jaar) !
    """

    location_ids = ["KW215712", "KW322613"]
    parameter_ids = ["Q.B.y", "DD.y"]
    start_time = datetime(2005, 1, 1)
    end_time = datetime(2023, 1, 1)

    # KW215712 DD.y  -> 2005-12-31 tm 2022-12-31
    # KW215712 Q.B.y -> 2006-12-31 tm 2022-12-31
    # KW322613 Q.B.y -> 2004-12-31 tm 2022-12-31
    # KW322613 DD.y  -> 2005-12-31 tm 2022-12-31
