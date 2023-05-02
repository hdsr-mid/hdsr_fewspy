from dataclasses import dataclass

import pandas as pd


@dataclass
class RequestSettings:
    max_request_nr_timestamps: int  # parse_raw(xml=response.text) takes 4 sec with 96054 timestamps
    min_request_nr_timestamps: int
    max_request_period: pd.Timedelta
    default_request_period: pd.Timedelta = None
    min_time_between_requests: pd.Timedelta = None
    max_response_time: pd.Timedelta = None  # Warn if response time is above and adapt next request
    updated_request_period: pd.Timedelta = None


def get_default_request_settings():
    return RequestSettings(
        max_request_nr_timestamps=100000,
        min_request_nr_timestamps=10000,
        max_request_period=pd.Timedelta(weeks=52 * 2),
        default_request_period=pd.Timedelta(weeks=8),
        min_time_between_requests=pd.Timedelta(seconds=1),
        max_response_time=pd.Timedelta(seconds=20),
    )
