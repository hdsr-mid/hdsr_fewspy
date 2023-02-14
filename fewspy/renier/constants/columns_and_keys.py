from gapfinder.hdsr_hkvfewspy.pi_rest import TimeSeriesCols
from gapfinder.utils import get_class_attributes
from hdsr_wis_config_reader.idmappings.columns import IdMapCols
from hdsr_wis_config_reader.idmappings.columns import StartEndDateCols
from typing import List
from typing import Tuple

import pandas as pd


class MetaInnerKeys:

    xml_start = "xml_start"
    xml_end = "xml_end"
    wis_start = "wis_start"
    wis_end = "wis_end"
    nr_missing_values = "nr_missing_values"
    nr_unwanted_flags = "nr_unwanted_flags"
    sum_normal_gaps_hours = "sum_normal_gaps_hours"
    sum_normal_gaps_days = "sum_normal_gaps_days"
    sum_normal_gaps_weeks = "sum_normal_gaps_weeks"
    sum_quarter_gaps_hours = "sum_quarter_gaps_hours"
    sum_quarter_gaps_days = "sum_quarter_gaps_days"
    sum_quarter_gaps_weeks = "sum_quarter_gaps_weeks"


# ts_analyser_columns
class TsAnalyserCols:
    nr_log_past_window = "nr_log_past_window"
    is_start_gap = "col_is_start_gap"
    is_end_gap = "col_is_end_gap"
    diff = "diff"
    redis_str = "redis_str"
    date_time = TimeSeriesCols.date_time
    value = TimeSeriesCols.value
    flag = TimeSeriesCols.flag


class RedisOuterKeys:

    meta = "meta"
    normal_gaps = "normal-gaps"
    quarter_gaps = "quarter-gaps"
    histogram_normal_hours = "histogram-normal-hours"
    histogram_normal_days = "histogram-normal-days"
    histogram_normal_weeks = "histogram-normal-weeks"
    histogram_quarter_hours = "histogram-quarter-hours"
    histogram_quarter_days = "histogram-quarter-days"
    histogram_quarter_weeks = "histogram-quarter-weeks"
    ts_analyse_fail = "ts-analyse-fail"
    ts_classify_fail = "ts-classify-fail"
    ts_classify_subloc_fail = "ts-classify-subloc-fail"
    classified_periods = "classified-periods"
    classified_merged_periods = "classified-merged-periods"
    classified_subloc = "classified-subloc"
    classified_subloc_discharge = "classified-subloc-discharge"
    hoofdloc_renovation_merged = "hoofdloc-renovation-merged"

    @classmethod
    def get_short_prefix(cls, histogram_key: str) -> str:
        mapper = {
            cls.histogram_normal_hours: "_h_",  # sorted(["d", "_h", "w"]) = ['_h', 'd', 'w']
            cls.histogram_normal_days: "d_",
            cls.histogram_normal_weeks: "w_",
            cls.histogram_quarter_hours: "_h_",
            cls.histogram_quarter_days: "d_",
            cls.histogram_quarter_weeks: "w_",
        }
        for outer_key, prefix in mapper.items():
            if outer_key in histogram_key:
                return prefix

    @classmethod
    def get_all(cls) -> List[str]:
        return list(get_class_attributes(the_class=cls).values())

    @classmethod
    def get_all_hist(cls) -> List[str]:
        a = [x for x in cls.get_all() if "histogram" in x]
        return a

    @classmethod
    def uuid(cls, row: pd.Series) -> str:
        ex_loc = row[IdMapCols.ex_loc]
        ex_par = row[IdMapCols.ex_par]
        int_loc = row[IdMapCols.int_loc]
        int_par = row[IdMapCols.int_par]
        return f"{ex_loc}_{ex_par}_{int_loc}_{int_par}"

    @classmethod
    def uuid_to_idmap_cols(cls, uuid: str) -> Tuple[str, str, str, str]:
        ex_loc, ex_par, int_loc, int_par = uuid.split("_")
        return ex_loc, ex_par, int_loc, int_par

    @classmethod
    def key_meta(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.meta}"

    @classmethod
    def key_normal_gaps(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.normal_gaps}"

    @classmethod
    def key_quarter_gaps(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.quarter_gaps}"

    @classmethod
    def key_normal_hist_hours(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_normal_hours}"

    @classmethod
    def key_normal_hist_days(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_normal_days}"

    @classmethod
    def key_normal_hist_weeks(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_normal_weeks}"

    @classmethod
    def key_quarter_hist_hours(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_quarter_hours}"

    @classmethod
    def key_quarter_hist_days(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_quarter_days}"

    @classmethod
    def key_quarter_hist_weeks(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.histogram_quarter_weeks}"

    @classmethod
    def key_ts_analyse_fail(cls, row: pd.Series) -> str:
        return f"{cls.uuid(row=row)}:{cls.ts_analyse_fail}"

    @classmethod
    def key_ts_classify_fail(cls, int_loc_par: str) -> str:
        return f"{int_loc_par}:{cls.ts_classify_fail}"

    @classmethod
    def key_ts_classify_subloc_fail(cls, int_loc: str) -> str:
        return f"{int_loc}:{cls.ts_classify_subloc_fail}"

    @classmethod
    def validate_key(cls, outer_key: str, _type: str) -> None:
        uuid, outer_key_type = outer_key.split(":")
        try:
            assert outer_key_type == _type, "outer_key_type == _type"
            assert outer_key_type in cls.get_all(), "outer_key_type in cls.get_all()"
            assert len(outer_key.split("_")) == 4, "len(outer_key.split('_')) == 4"
        except Exception as err:
            raise AssertionError(f"validate_key error: outer_key={outer_key}, _type={_type}, err={err}")


class GapCols:
    start = StartEndDateCols.start
    end = StartEndDateCols.end
    diff = TsAnalyserCols.diff

    @classmethod
    def get_all(cls) -> List[str]:
        return list(get_class_attributes(the_class=cls).values())
