from fewspy.renier.collector.filters import get_filters

import logging
import sys


def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    minor_min = 6
    minor_max = 9
    if major == 3 and minor_min <= minor <= minor_max:
        return
    raise AssertionError(f"your python version = {major}.{minor}. Please use python 3.{minor_min} to 3.{minor_max}")


def setup_logging() -> None:
    """Adds a configured strearm handler to the root logger."""
    log_level = logging.DEBUG
    log_date_format = "%H:%M:%S"
    log_format = "%(asctime)s %(filename)s %(levelname)s %(message)s"

    _logger = logging.getLogger()
    _logger.setLevel(log_level)
    formatter = logging.Formatter(fmt=log_format, datefmt=log_date_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)


if __name__ == "__main__":
    check_python_version()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("starting app")

    from datetime import datetime
    from fewspy.daniel.src.fewspy.api import Api

    url = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"
    filter_id = "INTERNAL-API"
    # KW431510
    # OW433001 H.G.O loopt van 29 sep 2011 tm 17 jan 2023 (filters: WIS/Werkfilter, WIS/Metingenfilter, HDSR/CAW)
    LOCATION_IDS = ["OW433001"]
    PARAMETER_IDS = ["H.G.0"]
    start_time = datetime(2022, 5, 1)
    end_time = datetime(2022, 5, 5)

    # daniel
    # url = ""https://www.hydrobase.nl/fews/nzv/FewsWebServices/rest/fewspiservice/v1/""
    # filter_id = "WDB_OW_KGM",
    # LOCATION_IDS = [
    #     "NL34.HL.KGM154.LWZ1",
    #     "NL34.HL.KGM154.HWZ1",
    #     "NL34.HL.KGM154.KWK",
    #     "NL34.HL.KGM156.PMP2",
    #     "NL34.HL.KGM156.HWZ1",
    #     "NL34.HL.KGM155.HWZ1",
    #     "NL34.HL.KGM156.KSL1",
    #     "NL34.HL.KGM156.LWZ1",
    #     "NL34.HL.KGM156.PMP1",
    #     "NL34.HL.KGM154.PMP1",
    #     "NL34.HL.KGM155.LWZ1",
    # ]
    # PARAMETER_IDS = ["Q [m3/s] [NVT] [OW]", "WATHTE [m] [NAP] [OW]"]

    api = Api(base_url=url)
    time_series_set = api.get_time_series(
        filter_id=filter_id,
        location_ids=LOCATION_IDS,
        start_time=start_time,
        end_time=end_time,
        parameter_ids=PARAMETER_IDS,
    )
    time_series_set = api.get_time_series(
        filter_id=filter_id,
        location_ids=LOCATION_IDS,
        start_time=start_time,
        end_time=end_time,
        parameter_ids=PARAMETER_IDS,
        parallel=True,
    )

    logger.info("shutting down app")
