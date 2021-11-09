from collector import constants
from collector.backends import get_pi_rest_instance

import pandas as pd


def get_filters() -> pd.DataFrame:
    pi = get_pi_rest_instance()
    pi.setQueryParameters(protocol=constants.PIWEBSERVICE_PROTOCOL)
    return pi.getFilters()
