from hdsr_fewspy.constants.request_settings import RequestSettings
from typing import List
from typing import Tuple

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class DateFrequencyBuilder:
    @classmethod
    def create_date_ranges_and_frequency_used(
        cls, startdate_obj: pd.Timestamp, enddate_obj: pd.Timestamp, frequency: pd.Timedelta
    ) -> Tuple[List[Tuple[pd.Timestamp, pd.Timestamp]], pd.Timedelta]:
        """
        Example:
            startdate_obj = pd.Timestamp("2010-04-27 00:00:00")
            enddate_obj = pd.Timestamp("2010-04-27 05:00:00")
            frequency = pd.Timedelta(hours=1, seconds=10, milliseconds=100)
            returns:
               date_range_tuples = [
                    (pd.Timestamp("2010-04-27 00:00:00"), pd.Timestamp("2010-04-27 01:00:10")), # diff = frequency_used
                    (pd.Timestamp("2010-04-27 01:00:10"), pd.Timestamp("2010-04-27 02:00:20")), # diff = frequency_used
                    (pd.Timestamp("2010-04-27 02:00:20"), pd.Timestamp("2010-04-27 03:00:30")), # diff = frequency_used
                    (pd.Timestamp("2010-04-27 03:00:30"), pd.Timestamp("2010-04-27 04:00:40")), # diff = frequency_used
                    (pd.Timestamp("2010-04-27 04:00:40"), pd.Timestamp("2010-04-27 05:00:00")), # diff <= frequency_used
                    ]
                frequency_used = pd.Timedelta("0 days 01:00:10")  # note that no milliseconds exist
        """
        # snap frequency to whole seconds
        frequency_used = frequency.round(pd.Timedelta(seconds=1))
        _range = pd.date_range(start=startdate_obj, end=enddate_obj, freq=frequency_used)
        # add enddate_obj to range
        _range = _range.union([enddate_obj])
        date_range_tuples = []
        for index, date_str in enumerate(_range):
            try:
                start_str = _range[index]
                end_str = _range[index + 1]
                _tuple = pd.Timestamp(start_str), pd.Timestamp(end_str)
                date_range_tuples.append(_tuple)
            except IndexError:
                logger.debug("no more dates left over")
        return date_range_tuples, frequency_used

    @staticmethod
    def log_progress_download_ts(
        data_range_start: pd.Timestamp, data_range_end: pd.Timestamp, ts_end: pd.Timestamp
    ) -> None:
        """Compare request_enddate (which chances over time) with time-series start end (no change over time)."""
        _end_max_today = min(pd.Timestamp.now(tz=data_range_end.tz), data_range_end)
        timedelta_total_ts = _end_max_today - data_range_start
        timedelta_so_far = ts_end - data_range_start
        progress_percentage = round(timedelta_so_far / timedelta_total_ts * 100, 2)
        logger.info(f"download time-series progress={progress_percentage}%")

    @staticmethod
    def optional_change_date_range_freq(
        nr_timestamps: int,
        date_range_freq: pd.Timedelta,
        request_settings: RequestSettings,
        startdate_request: pd.Timestamp,
        enddate_request: pd.Timestamp,
    ) -> pd.Timedelta:
        """Optional increase or decrease the time-window of a request depending on nr_timestamps found."""
        if nr_timestamps > request_settings.max_request_nr_timestamps:
            date_range_freq = 0.7 * date_range_freq
        elif nr_timestamps < request_settings.min_request_nr_timestamps:
            if date_range_freq > request_settings.max_request_period:
                logger.debug(
                    f"date_range_freq={date_range_freq} exceeds max_request_period="
                    f"(={request_settings.max_request_period}). Continue with date_range_freq={date_range_freq}"
                )
                return date_range_freq
            period_required = enddate_request - startdate_request
            if date_range_freq > period_required:
                logger.debug(
                    f"date_range_freq={date_range_freq} exceeds period available (={period_required}). Continue with "
                    f"date_range_freq={date_range_freq}"
                )
                return date_range_freq

            try:
                date_range_freq = 1.3 * date_range_freq
            except (OverflowError, pd.errors.OutOfBoundsDatetime) as err:
                logger.debug(
                    f"could not increase date_range_freq (err={err}). Continue with date_range_freq={date_range_freq}"
                )
        return date_range_freq
