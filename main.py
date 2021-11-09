from collector.timeseries import get_filters

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

    # TODO: do something useful here
    df_filters = get_filters()
    assert not df_filters.empty

    logger.info("shutting down app")
