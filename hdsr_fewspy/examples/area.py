from datetime import datetime

import hdsr_fewspy
import logging


logger = logging.getLogger(__name__)


def run_example_area():
    """
    Get soilmoisture, precipitation and evaporation time-series aggregated to an area.

    Areas can be afvoergebied or peilgebied. In example below we use afvoergebied with id 'AFVG13'.
    Use api.get_locations() to get an overview of area ids.
    Note that the areas (.shp) are old (from 2011).

    code below results in logging:
        df wis_production_area_soilmoisture 638 rows from 2019-12-31 till 2022-12-31
        df wis_production_area_precipitation_wiwb 26269 rows from 2020-01-01 till 2023-01-01
        df wis_production_area_precipitation_radarcorrection 4425 rows from 2020-01-01 till 2020-07-03
        df wis_production_area_evaporation_wiwb_satdata 1036 rows from 2020-01-01 till 2023-01-01
        df wis_production_area_evaporation_waterwatch 2717 rows from 2011-03-30 till 2019-12-29
    """
    setup_logging()

    logger.info("start run_example_point")

    # bodemvocht
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_soilmoisture,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="SM.d",
        qualifier_id="Lband05cm",  # ["Lband05cm", "Lband10cm", "Lband20cm"]
        start_time=datetime(year=2020, month=1, day=1),
        end_time=datetime(year=2023, month=1, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    logger.info(
        f"df wis_production_area_soilmoisture {len(df)} rows from {df.index.date.min()} till {df.index.date.max()}"
    )

    # neerslag wiwb (tot 2019)
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_precipitation_wiwb,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="Rh.h",
        qualifier_id="wiwb_merge",  # choose from ["wiwb_merge"]
        start_time=datetime(year=2020, month=1, day=1),
        end_time=datetime(year=2023, month=1, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    logger.info(
        f"df wis_production_area_precipitation_wiwb {len(df)} rows from {df.index.date.min()} till "
        f"{df.index.date.max()}"
    )

    # neerslag radarcorrection (vanaf 2019)
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_precipitation_radarcorrection,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="Rh.h",
        qualifier_id="mfbs_merge",  # choose from ["mfbs_merge"]
        start_time=datetime(year=2020, month=1, day=1),
        end_time=datetime(year=2023, month=1, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    logger.info(
        f"df wis_production_area_precipitation_radarcorrection {len(df)} rows from {df.index.date.min()} "
        f"till {df.index.date.max()}"
    )

    # verdamping wiwb satdata
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_evaporation_wiwb_satdata,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="Eact.d",
        qualifier_id="RA",  # choose from ["RA", "satdata_merge", ""]
        start_time=datetime(year=2020, month=1, day=1),
        end_time=datetime(year=2023, month=1, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    logger.info(
        f"df wis_production_area_evaporation_wiwb_satdata {len(df)} rows from {df.index.date.min()} till "
        f"{df.index.date.max()}"
    )

    # verdamping waterwatch
    api = hdsr_fewspy.Api(
        pi_settings=hdsr_fewspy.DefaultPiSettingsChoices.wis_production_area_evaporation_waterwatch,
    )
    df = api.get_time_series_single(
        location_id="AFVG13",
        parameter_id="Eact.d",
        qualifier_id="",  # choose from [""]
        start_time=datetime(year=2000, month=1, day=1),
        end_time=datetime(year=2023, month=1, day=1),
        drop_missing_values=True,
        output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory,
    )
    logger.info(
        f"df wis_production_area_evaporation_waterwatch {len(df)} rows from {df.index.date.min()} till "
        f"{df.index.date.max()}"
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
