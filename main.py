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


# TODO: Use BackoffRetry strategy

# TODO: add rate_limiting to requests (freq and size)

# TODO: don't use strings as urls...

# TODO: authenticate by GET request a hdsr-mid repo (yet to build) that holds email_token items per user

# TODO: test other get requests than get_timeseries

# TODO: create documentation


if __name__ == "__main__":
    check_python_version()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("starting app")

    logger.info("shutting down app")
