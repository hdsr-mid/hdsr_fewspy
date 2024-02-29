from geopandas import GeoSeries
from logging.handlers import RotatingFileHandler
from shapely.geometry import box
from shapely.geometry import Point
from wiwb.sample import sample_nc_dir

import logging
import sys


def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    minor_min = 7
    minor_max = 12
    if major == 3 and minor_min <= minor <= minor_max:
        return
    raise AssertionError(f"your python version = {major}.{minor}. Please use python 3.{minor_min} to 3.{minor_max}")


def setup_logging() -> None:
    """Adds 2 configured handlers (rotating file + stream) to the root logger."""
    # constants
    stream_log_level = logging.INFO
    stream_log_format = logging.Formatter(fmt="%(asctime)s %(filename)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    file_log_level = logging.INFO
    file_log_format = logging.Formatter(
        fmt="%(asctime)s %(filename)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # handler: stream
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(stream_log_level)
    stream_handler.setFormatter(stream_log_format)

    # root logger
    root_logger = logging.getLogger()
    lowest_required_log_level = min(stream_log_level, file_log_level)
    root_logger.setLevel(lowest_required_log_level)
    root_logger.addHandler(stream_handler)
    root_logger.info("setup logging done")


def add_points_to_grids(grids):
    LL_POINT = Point(119865, 449665)
    UR_POINT = Point(127325, 453565)
    OTHER_POINT = Point(135125, 453394)
    POLYGON = box(LL_POINT.x, LL_POINT.y, UR_POINT.x, UR_POINT.y)
    GEOSERIES = GeoSeries(
        [LL_POINT, UR_POINT, OTHER_POINT, POLYGON], index=["ll_point", "ur_point", "other_point", "polygon"], crs=28992
    )

    grids.geometries = GEOSERIES
    # TODO: @daniel: zit hier een check op GEOSERIES binnen bounding box van grids valt?

    return grids


if __name__ == "__main__":
    check_python_version()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("starting app")

    from datetime import date
    from datetime import datetime
    from pathlib import Path
    from wiwb.api import Api
    from wiwb.api_calls.get_grids import GetGrids
    from wiwb.auth import Auth

    TMP_OUTPUT_DIR = Path("./tmp_output_dir")
    assert TMP_OUTPUT_DIR.is_dir()

    wiwb_client_id = "api-wiwb-hdsr-tollenaar-tmp"
    wiwb_client_secret = "Yz8Rrmc36TJ21FTLnKpVb6AMEY3oJUzS"
    auth = Auth(client_id=wiwb_client_id, client_secret=wiwb_client_secret)

    api = Api(auth=auth)

    data_sources = api.get_data_sources()
    print(sorted(data_sources.keys()))
    # [
    # 'Knmi.International.Radar.Composite',
    # 'Knmi.International.Radar.Composite.Combined',
    # 'Knmi.International.Radar.Composite.Early.Reanalysis',
    # 'Knmi.International.Radar.Composite.Early.Reanalysis.Test',
    # 'Knmi.International.Radar.Composite.Final.Reanalysis',
    # 'Knmi.International.Radar.Composite.Final.Reanalysis.Test',
    # 'Knmi.International.Radar.Composite.Near.Realtime.Test',
    # 'Knmi.Radar.CorrectedB',
    # 'Knmi.Radar.CorrectedC2',
    # 'Knmi.Radar.CorrectedD2',
    # 'Knmi.Radar.Uncorrected',
    # 'Meteobase.Evaporation.Makkink',
    # 'Meteobase.Evaporation.PennmanMonteith',
    # 'Meteobase.Precipitation',
    # 'Satdata.Evapotranspiration.Reanalysis',
    # 'Satdata.Evapotranspiration.Reanalysis.V2'
    # ]

    variables = api.get_variables(data_source_codes=["Meteobase.Precipitation"])
    print(variables)
    # {'P': {'Name': 'Precipitation', 'Code': 'P', 'Description': 'Neerslag', 'UnitCode': 'MM', 'State': 1}}

    grids = GetGrids(
        auth=auth,
        base_url=api.base_url,
        data_source_code="Meteobase.Precipitation",
        variable_code="P",
        start_date=date(2018, 1, 1),
        end_date=date(2018, 1, 2),
        data_format_code="netcdf4.cf1p6",
    )

    grids.run()
    # grids.write(output_dir=TMP_OUTPUT_DIR.as_posix())  # .nc in TMP_OUTPUT_DIR van 49 kb

    grids = add_points_to_grids(grids)

    df = grids.sample()
    _now = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_path = TMP_OUTPUT_DIR / f"samples_{_now}.csv"
    df.to_csv(csv_file_path.as_posix())

    # het is momenteel alleen mogelijk om .nc te resamplen (niet .geotiff)
    H_DRIVE = Path("H:/")
    dir_path_vdsat = H_DRIVE / "DATA/WIWB_grids/VanderSat_Bodemvocht_HDSR"
    vd_sat_a = dir_path_vdsat / "DRZSM-SMAP-LN-DESC-T10_V003_100"
    vd_sat_b = dir_path_vdsat / "DRZSM-SMAP-LN-DESC-T20_V003_100"
    vd_sat_c = dir_path_vdsat / "SM-SMAP-LN-DESC_V003_100"

    for i in [vd_sat_a, vd_sat_b, vd_sat_c]:
        assert i.is_dir()

    # get variables from directory names and take the first
    LL_POINT = Point(119865, 449665)
    UR_POINT = Point(127325, 453565)
    OTHER_POINT = Point(135125, 453394)
    POLYGON = box(LL_POINT.x, LL_POINT.y, UR_POINT.x, UR_POINT.y)
    GEOSERIES = GeoSeries(
        [LL_POINT, UR_POINT, OTHER_POINT, POLYGON], index=["ll_point", "ur_point", "other_point", "polygon"], crs=28992
    )

    sample_nc_dir(
        dir=vd_sat_a / "Complete_files",
        variable_code="DRZSM-SMAP-LN-DESC-T10_V003_100",
        geometries=GEOSERIES,
        stats="mean",
        start_date=None,
        end_date=None,
    )

    logger.info("shutting down app")
