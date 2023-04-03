from datetime import datetime
from fewspy.constants.choices import TimeZoneChoices
from fewspy.constants.paths import BASE_DIR
from fewspy.tests.fixtures import api_sa_fixture

import json


# silence flake8
api_sa_fixture = api_sa_fixture


class RequestData1:
    filter_id = "INTERNAL-API"
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


def test_sa_timezone_response(api_sa_fixture):
    tz_id = api_sa_fixture.get_timezone_id()
    assert tz_id in TimeZoneChoices.get_all()
    assert tz_id == TimeZoneChoices.gmt.value
