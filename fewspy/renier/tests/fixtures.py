from gapfinder.analysers.gaps.manager import TimeSeriesAnalyseManager
from gapfinder.constants.webservices import StandAloneWebServiceSettings
from gapfinder.hdsr_hkvfewspy.pi_rest import HdsrPiRest
from gapfinder.hdsr_hkvfewspy.pi_rest import TimeSeriesCols
from gapfinder.storage.redis_choices import LocalRedisTest
from typing import Dict

import pandas as pd
import pytest
import pytz


df_wis_ts = pd.DataFrame(
    # define outside function/class to keep code+comments on same row (readability) otherwise tool black creates a mess
    data={
        TimeSeriesCols.date_time: {  # noqa                 flag  value comment
            0: pd.Timestamp("2011-09-29 00:00:00+0000"),  # 0     0
            1: pd.Timestamp("2011-09-29 00:13:59+0000"),  # 0     0
            2: pd.Timestamp("2011-09-29 00:16:00+0000"),  # 0     0
            3: pd.Timestamp("2011-09-29 00:30:00+0000"),  # 0     0     1 quarter_gap [00:14:00-00:16:00]
            4: pd.Timestamp("2011-09-29 00:45:00+0000"),  # 0     0
            5: pd.Timestamp("2011-09-29 00:59:07+0000"),  # 5     0     excluded flag
            6: pd.Timestamp("2011-09-29 01:00:20+0000"),  # 0     -999  excluded value
            7: pd.Timestamp("2011-09-29 01:14:04+0000"),  # 0     0     1 quarter_gap [00:59:00-01:01:00]
            8: pd.Timestamp("2011-09-29 01:30:00+0000"),  # 0     0
            9: pd.Timestamp("2011-09-29 01:43:59+0000"),  # 0     0
            10: pd.Timestamp("2011-09-29 01:44:00+0000"),  # 0    0
            11: pd.Timestamp("2011-09-29 02:00:59+0000"),  # 0    0     not a quarter_gap (just within limit)
            12: pd.Timestamp("2011-09-29 02:01:00+0000"),  # 0    0
            13: pd.Timestamp("2011-09-29 02:15:00+0000"),  # 0    0     1 30min quarter_gap (45min and 00min)
            14: pd.Timestamp("2011-09-29 03:00:00+0000"),  # 0    0     1 quarter_gap of 45 minutes
            15: pd.Timestamp("2011-09-29 05:00:00+0000"),  # 0    0     not a normal_gap as (as not >2h)
            16: pd.Timestamp("2011-09-29 07:01:00+0000"),  # 0    0     1 2h1min normal_gap and multi quarter_gaps
            17: pd.Timestamp("2011-09-29 08:00:00+0000"),  # 0
            18: pd.Timestamp("2011-09-29 11:00:00+0000"),  # 6    0     excluded flag
            19: pd.Timestamp("2011-09-29 12:00:00+0000"),  # 0    -999  excluded value
            20: pd.Timestamp("2011-09-29 20:00:00+0000"),  # 0    0     1 12h normal_gap [8-20] and multi quarter_gaps
        }
    }
)


def get_df_wis_ts() -> pd.DataFrame:
    assert df_wis_ts[TimeSeriesCols.date_time].dt.tz == pytz.utc
    df_wis_ts[TimeSeriesCols.flag] = 0
    df_wis_ts.loc[5, TimeSeriesCols.flag] = 5
    df_wis_ts.loc[18, TimeSeriesCols.flag] = 6
    df_wis_ts[TimeSeriesCols.value] = 0
    df_wis_ts.loc[6, TimeSeriesCols.value] = -999
    df_wis_ts.loc[19, TimeSeriesCols.value] = -999
    df_wis_ts[TimeSeriesCols.moduleInstanceId] = "WerkFilter"
    df_wis_ts[TimeSeriesCols.qualifierId] = ""
    df_wis_ts[TimeSeriesCols.parameterId] = "F.0"
    df_wis_ts[TimeSeriesCols.units] = "Hz"
    df_wis_ts[TimeSeriesCols.locationId] = "KW100111"
    df_wis_ts[TimeSeriesCols.stationName] = "WIJKERSLOOT_1001-K_WIJKERSLOOT-pompvijzel1_aanvoer"
    df_wis_ts[TimeSeriesCols.user] = "user"
    return df_wis_ts


@pytest.fixture(scope="session")
def ts_analyser_fixture() -> TimeSeriesAnalyseManager:
    pi_rest_settings = StandAloneWebServiceSettings()
    manager = TimeSeriesAnalyseManager(
        uuid="xx",
        max_normal_gap_allowed=pd.Timedelta(hours=2),
        pi_rest_settings=pi_rest_settings,
    )
    manager.add_df_time_series(df_ts=get_df_wis_ts())
    manager.run()
    return manager


@pytest.fixture()
def loc_date_query_parameters_kw100111_f0() -> Dict:
    """
    series                             001_FQ1
    start                  2010-04-27 23:59:59
    end                    2018-03-27 13:15:00
    filename_start       HDSR_CAW_201204262000
    filename_end         HDSR_CAW_201803271320
    externalLocation                       001
    externalParameter                      FQ1
    internalLocation                  KW100111
    internalParameter                      F.0
    idmap_source                   IdOPVLWATER
    """
    return {
        "locationIds": ["KW100111"],
        "parameterIds": ["F.0"],
        # only get one day of time-series (after 2011 dec 31)
        "startTime": "2012-10-27 23:59:59",  # pd.Timestamp("2012-10-27 23:59:59").isoformat(sep="T") + "Z",
        "endTime": "2012-10-28 23:59:59",  # pd.Timestamp("2012-10-28 23:59:59").isoformat(sep="T") + "Z",
    }


@pytest.fixture()
def loc_date_query_parameters_ow100102_hg0() -> Dict:
    """
    series                             001_HB1
    start                  2010-04-27 23:59:59
    end                    2018-03-27 13:15:00
    filename_start       HDSR_CAW_201204262000
    filename_end         HDSR_CAW_201803271320
    externalLocation                       001
    externalParameter                      HB1
    internalLocation                  OW100102
    internalParameter                    H.G.0
    idmap_source                   IdOPVLWATER
    """
    return {
        "locationIds": ["OW100102"],
        "parameterIds": ["H.G.0"],
        # only get one day of time-series (after 2011 dec 31)
        "startTime": "2012-10-27 23:59:59",  # pd.Timestamp("2012-10-27 23:59:59").isoformat(sep="T") + "Z",
        "endTime": "2012-10-28 23:59:59",  # pd.Timestamp("2012-10-28 23:59:59").isoformat(sep="T") + "Z",
    }


@pytest.fixture(scope="session")
def stand_alone_pi_rest() -> HdsrPiRest:
    pi_rest = HdsrPiRest(use_stand_alone_webservice=True)
    assert pi_rest.settings.base_url == "http://localhost:8081/FewsWebServices/rest/fewspiservice/v1/"
    assert pi_rest.settings.module_instance_id == "ImportOpvlWater"
    assert pi_rest.settings.filter_id == "INTERAL-API.RUW_OPVL"
    return pi_rest


@pytest.fixture(scope="session")
def production_pi_rest() -> HdsrPiRest:
    pi_rest = HdsrPiRest(use_stand_alone_webservice=False)
    return pi_rest


@pytest.fixture(scope="function")
def redis_test_db() -> LocalRedisTest:
    return LocalRedisTest()
