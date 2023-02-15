from config import api
from pathlib import Path

import json


DATA_PATH = Path(__file__).parent / "data"

with open(DATA_PATH / "filters.json") as src:
    filter_reference = json.load(src)
filters = api.get_filters()


def test_to_reference_set():
    assert filter_reference == filters
