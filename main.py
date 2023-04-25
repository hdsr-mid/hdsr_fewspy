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
    """Adds a configured stream handler to the root logger."""
    log_level = logging.INFO
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
    logger.info("shutting down app")


# DONE: Use BackoffRetry strategy

# DONE: add rate_limiting to requests (freq and size)

# TODO: don't use strings as urls...

# Done: authenticate by GET request a hdsr-mid repo (yet to build) that holds email_token items per user

# DONE: test other get requests than get_timeseries

# TODO: create documentation

# DONE: enable users to override Api.pi_settings

# DONE: conversion client - server timezone

# DONE: fix moduleInstanceIds and filterId

# DONE: wat als iemand alleen maar statistieken wil van tijdseries?

# TODO: besides allowed_request_args use a required_request_args (get_locations zonder filter duurt tering lang!!)

# TODO: create pypi package (delete main.py etc)


# TODO: Ciska wel interesse wel in:
#  --------------------------------
#  get_samples (grote request)
#  - Deltares is hier begin 2024 klaar. Nu geeft FEWS EFICS piwebservice na 2 of 5 minuten een timeout
#  get_timeseries (grote request)
#  - altijd start + end
#  - altijd omitEmptyTimeSeries op True anders geeft ie minimaal weken aan tijdseries terug
#  - vaak filter_id
#  - soms parameter_id, location_id, moduleinstance_id
#  - heel soms qualifier_id
#  get_parameters (middlegrote request = 400 parameters)
#  get_locations (kleine request = 300 locaties)
#

# TODO: Ciska geen interesse in:
#  --------------------------------
#  get_qualifiers

# TODO: check of properties goed meekomen in get_timeseries in PI_JSON (in PI_XML gaat het goed) -> Ciska:" bij
#  EFICS werkt niet helemaal lekker. bij get_samples gaat het helemaal fout"

# TODO: potentieel van grote naar kleine belasting (retry-backoff nodig): get_samples, get_timeseries,
#  get_qualifiers (25 groepen * 100k regels per groep), get_parameters (4000), get_locations (300)

# TODO: use onlyHeader=True kan voor get_timeseries en get_samples (beide hebben ook start + eind).
#  Echter, get_qualifiers heeft dat niet. FEWS-WIS response is snel (<1sec). FEWS-EFICS duurt lang (8 sec)
#  get_lcoations duurt 7 sec.
#  Voorstel Ciska: alleen func get_timeseries + get_samples via PiWebService. De andere request disabelen:
#  logger.info('Stuur ciska.overbeek@hdsr.nl een mailtje of dat lijstje mag, dan krijg je er ook nog meer info bij)
#  die lijstjes worden 2 a 3 per jaar script + handmatig ge-update.

# TODO: add usage examples to readme.md
#  pip install hdsr_fewspy
#  user + token
#  request naar repo met bovenstaande csv (check)
#  api = Api(user=rob, token=adsfads;flkj, output_folder=..., convert_output_to_csv=False)
#  response = api.get_time_series(parameter_ids=['H.G.0'])
#  # TODO: voor Ciska belangrijk dat er een xml uitkomt
