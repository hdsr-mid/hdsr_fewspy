from collector import constants
from collector.backends import get_pi_rest_instance

import logging
import pandas as pd


logger = logging.getLogger(__name__)


def get_filters() -> pd.DataFrame:
    pi = get_pi_rest_instance()
    logger.debug("setting query parameters for getFilters()")
    pi.setQueryParameters(protocol=constants.PIWEBSERVICE_PROTOCOL)
    return pi.getFilters()
