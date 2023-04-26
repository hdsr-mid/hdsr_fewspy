from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from hdsr_fewspy.constants.choices import TimeZoneChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.converters.utils import camel_to_snake_case
from hdsr_fewspy.converters.utils import dict_to_datetime
from typing import List
from typing import Tuple

import pandas as pd


DATETIME_KEYS = ["start_date", "end_date"]
FLOAT_KEYS = ["miss_val", "lat", "lon", "x", "y", "z"]
EVENT_COLUMNS = ["datetime", "value", "flag"]


@dataclass
class Header:
    """FEWS-PI header-style dataclass"""

    type: str
    module_instance_id: str
    location_id: str
    parameter_id: str
    time_step: dict
    start_date: datetime
    end_date: datetime
    miss_val: float
    lat: float
    lon: float
    x: float
    y: float
    units: str
    station_name: str = None
    z: float = None
    qualifier_id: List[str] = None

    @classmethod
    def from_pi_header(cls, pi_header: dict) -> Header:
        """Parse Header from FEWS PI header dict.
        Args:
            pi_header (dict): FEWS PI header as dictionary
        Returns:
            Header: FEWS-PI header-style dataclass
        """

        def _convert_kv(k: str, v) -> Tuple:
            k = camel_to_snake_case(k)
            if k in DATETIME_KEYS:
                v = dict_to_datetime(v)
            if k in FLOAT_KEYS:
                v = float(v)
            return k, v

        args = (_convert_kv(k, v) for k, v in pi_header.items())
        header = Header(**{i[0]: i[1] for i in args if i[0] in cls.__dataclass_fields__.keys()})  # noqa
        return header


class Events(pd.DataFrame):
    """FEWS-PI events in pandas DataFrame"""

    @classmethod
    def from_pi_events(
        cls,
        pi_events: list,
        missing_value: float,
        drop_missing_values: bool,
        flag_threshold: int,
        tz_offset: float = None,
    ) -> Events:
        """Parse Events from FEWS PI events dict."""

        df = Events(data=pi_events)

        # set datetime
        if tz_offset is not None:
            df["datetime"] = pd.to_datetime(df["date"]) + pd.to_timedelta(df["time"]) - pd.Timedelta(hours=tz_offset)
        else:
            df["datetime"] = pd.to_datetime(df["date"]) + pd.to_timedelta(df["time"])

        # set value to numeric
        df["value"] = pd.to_numeric(df["value"])
        if drop_missing_values:
            # remove missings
            df = df.loc[df["value"] != missing_value]

        # drop columns and add missing columns
        drop_cols = [i for i in df.columns if i not in EVENT_COLUMNS]
        df.drop(columns=drop_cols, inplace=True)
        nan_cols = [i for i in EVENT_COLUMNS if i not in df.columns]
        df[nan_cols] = pd.NA

        # set flag to numeric
        df["flag"] = pd.to_numeric(df["flag"])
        if flag_threshold:
            # remove rows that have a unreliable flag: A flag_threshold of 6 means that only values with a
            # flag < 6 will be included
            df = df.loc[df["flag"] < flag_threshold]

        # set datetime to index
        df.set_index("datetime", inplace=True)

        return df


@dataclass
class TimeSeries:
    """FEWS-PI time series"""

    header: Header
    events: Events = pd.DataFrame(columns=EVENT_COLUMNS).set_index("datetime")

    @classmethod
    def from_pi_time_series(
        cls, pi_time_series: dict, drop_missing_values: bool, flag_threshold: int, time_zone: float = None
    ) -> TimeSeries:
        header = Header.from_pi_header(pi_header=pi_time_series["header"])
        kwargs = dict(header=header)
        if "events" in pi_time_series.keys():
            kwargs["events"] = Events.from_pi_events(
                pi_events=pi_time_series["events"],
                missing_value=header.miss_val,
                tz_offset=time_zone,
                drop_missing_values=drop_missing_values,
                flag_threshold=flag_threshold,
            )
        dc_timeseries = TimeSeries(**kwargs)
        return dc_timeseries


@dataclass
class TimeSeriesSet:
    version: str = None
    time_zone: float = None
    time_series: List[TimeSeries] = field(default_factory=list)

    def __len__(self):
        return len(self.time_series)

    @classmethod
    def from_pi_time_series(cls, pi_time_series: dict, drop_missing_values: bool, flag_threshold: int) -> TimeSeriesSet:
        kwargs = dict()
        kwargs["version"] = pi_time_series.get("version", None)

        time_zone = pi_time_series.get("timeZone", TimeZoneChoices.get_hdsr_default())
        time_zone_float = TimeZoneChoices.get_tz_float(value=time_zone)
        kwargs["time_zone"] = time_zone_float

        time_series = pi_time_series.get("timeSeries", [])
        kwargs["time_series"] = [
            TimeSeries.from_pi_time_series(
                pi_time_series=i,
                time_zone=kwargs["time_zone"],
                drop_missing_values=drop_missing_values,
                flag_threshold=flag_threshold,
            )
            for i in time_series
        ]
        dc_timeseriesset = cls(**kwargs)
        return dc_timeseriesset

    @property
    def is_empty(self) -> bool:
        return all([i.events.empty for i in self.time_series])

    @property
    def parameter_ids(self) -> List[str]:
        return list(set([i.header.parameter_id for i in self.time_series]))

    @property
    def location_ids(self) -> List[str]:
        return list(set([i.header.location_id for i in self.time_series]))

    @property
    def qualifier_ids(self) -> List[str]:
        qualifiers = (i.header.qualifier_id for i in self.time_series)
        qualifiers = [i for i in qualifiers if i is not None]
        flat_list = [i for j in qualifiers for i in j]
        return list(set(flat_list))


def response_jsons_to_one_df(
    responses: List[ResponseType], drop_missing_values: bool, flag_threshold: int
) -> pd.DataFrame:
    df = pd.DataFrame(data=None)
    for index, response in enumerate(responses):
        data = response.json()
        time_series_set = TimeSeriesSet.from_pi_time_series(
            pi_time_series=data, drop_missing_values=drop_missing_values, flag_threshold=flag_threshold
        )
        for time_series in time_series_set.time_series:
            _df = time_series.events
            _df["location_id"] = time_series_set.location_ids[0]
            _df["parameter_id"] = time_series_set.parameter_ids[0]
            if not df.empty:
                assert sorted(_df.columns) == sorted(df.columns), "code error"
            df = pd.concat(objs=[df, _df], axis=0)
    return df
