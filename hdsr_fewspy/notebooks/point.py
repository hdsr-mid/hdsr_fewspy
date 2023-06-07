from datetime import datetime
from pathlib import Path

import hdsr_fewspy
import logging


logger = logging.getLogger(__name__)


def run_example_point():
    """Get day/month discharge [m3/s] time-series (2015 till now) for the whole HDSR area."""

    # ["Q.G.y", "Q.G.m", "Q.B.y", "Q.B.m"]
    # raw = 20 csvs (alleen qg)
    # work = 18 csvs (alleen qb)
    # validated = 9 csvs (alleen qb)

    # "Q.G.d", "Q.G.m", "Q.B.d", "Q.B.m"]
    # raw = 20 csvs (alleen qg)
    # work = 18 csvs (alleen qb)
    # validated = 18 csvs (alleen qb)

    logger.info("start run_example_point")

    # prepare api
    dir_here = Path(__file__).parent
    api = hdsr_fewspy.Api(
        output_directory_root=dir_here, pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_point_validated
    )

    # determine locations
    df_all_locs = api.get_locations(output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory)
    df_kw_locs = df_all_locs[df_all_locs.index.str.startswith("KW")]
    locations = df_kw_locs.index.to_list()

    # ik vermoed dat de laatste download sessie is onderbroken (pycharm was afgesloten..)
    # ik heb geen logging file
    # laaste loc in dir hdsr_fewspy_20230601_130806_validated/ = KW446911
    # locations.index("KW446911")
    # 442
    # len(locations)
    # 1143
    # dus ergens op 1/3 is sessie onderbroken?
    # locations = locations[442:]

    # ik vermoed dat de laatste download sessie is onderbroken (pycharm was afgesloten..)
    # ik heb geen logging file
    # laaste loc in dir hdsr_fewspy_20230601_130806_validated/ = KW446911
    # locations.index("KW761201")
    # 1104
    # len(locations)
    # 1143
    # dus ergens op 96% is sessie onderbroken?
    locations = locations[1104:]

    # request data from Api
    api.get_time_series_multi(
        location_ids=locations,
        parameter_ids=["Q.G.d", "Q.G.m", "Q.B.d", "Q.B.m"],
        start_time=datetime(year=2015, month=1, day=1),
        end_time=datetime(year=2023, month=6, day=1),
        output_choice=hdsr_fewspy.OutputChoices.csv_file_in_download_dir,
    )


def setup_logging() -> None:
    """Adds a configured handler to the root logger: stream."""
    # handler: stream
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))

    # root logger (with 1 handler)
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(min([handler.level for handler in root_logger.handlers]))
    root_logger.info("setup logging done")


setup_logging()
run_example_point()
