from abc import abstractmethod
from datetime import datetime
from fewspy.api_calls.base import GetRequest
from fewspy.time_series import TimeSeriesSet
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.date_frequency import DateFrequencyBuilder
from typing import Dict
from typing import List
from typing import Tuple

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesBase(GetRequest):

    url_post_fix = "timeseries"

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        location_ids: str,
        parameter_ids: str,
        qualifier_ids: str = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
        return_pandas_dataframe: bool = True,
        *args,
        **kwargs,
    ):
        """
        Args:
            - start_time (datetime.datetime): datetime-object with start datetime to use in request.
            - end_time (datetime.datetime): datetime-object with end datetime to use in request.
            - location_ids (str): a FEWS location id to extract timeseries from.
            - parameter_ids (str): a FEWS parameter id to extract timeseries from.
            - qualifier_ids (str): a FEWS qualifier id to extract timeseries from. Defaults to None.
            - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
            - only_headers (bool): if True, only headers will be returned. Defaults to False.
            - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
            - omit_empty_timeseries (bool): if True, missing values (-999) are left out in response. Defaults to True.
            - drop_missing_values (bool): Defaults to False.
            - flag_threshold (int): Exclude unreliable values. Default to 6 (only values with flag<6 will be included).
            - return_pandas_dataframe (bool): Return timeseries in a panda DataFrame. Defaults to True.
        """
        super().__init__(*args, **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.location_ids = location_ids
        self.parameter_ids = parameter_ids
        self.qualifier_ids = qualifier_ids
        self.thinning = thinning
        self.only_headers = only_headers
        self.show_statistics = show_statistics
        self.omit_empty_timeseries = omit_empty_timeseries
        self.drop_missing_values = drop_missing_values
        self.flag_threshold = flag_threshold
        self.return_pandas_dataframe = return_pandas_dataframe

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _get_nr_timestamps(self, params: Dict) -> int:
        params["onlyHeaders"] = True
        params["showStatistics"] = True
        response = self.retry_backoff_session.get(url=self.url, params=params, verify=self.pi_settings.ssl_verify)
        if not response.ok:
            raise AssertionError(f"response not okay, status_code={response.status_code}, err={response.text}")
        timeseries = response.json().get("timeSeries", None)
        if not timeseries:
            return 0
        if len(timeseries) == 1:
            nr_timestamps = int(timeseries[0]["header"]["valueCount"])
            return nr_timestamps

        # error since too many timeseries
        msg = "Found multiple timeseries in _get_nr_timestamps"
        if "moduleInstanceIds" not in params:
            msg += (
                f"Please specify 1 moduleInstanceIds in pi_settings instead of '{self.pi_settings.module_instance_ids}'"
            )

        raise AssertionError(msg)

    def _download_timeseries(
        self,
        url: str,
        date_ranges: List[Tuple[pd.Timestamp, pd.Timestamp]],
        date_range_freq: pd.Timedelta,
        ts_startdate: pd.Timestamp,
        ts_enddate: pd.Timestamp,
        request_params: Dict,
        drop_missing_values: bool,
        flag_threshold: int,
    ) -> TimeSeriesSet:
        for request_index, (startdate_request, enddate_request) in enumerate(date_ranges):
            request_params["startTime"] = datetime_to_fews_str(startdate_request)
            request_params["endTime"] = datetime_to_fews_str(enddate_request)
            uuid = f"{request_params['locationIds'][0]} {request_params['parameterIds'][0]}"
            nr_timestamps_in_response = self._get_nr_timestamps(params=request_params)
            logger.debug(f"nr_timestamps_in_response={nr_timestamps_in_response}")
            new_date_range_freq = DateFrequencyBuilder.optional_change_date_range_freq(
                nr_timestamps=nr_timestamps_in_response,
                date_range_freq=date_range_freq,
                request_settings=request_settings,
                startdate_request=startdate_request,
                enddate_request=enddate_request,
            )
            create_new_date_ranges = new_date_range_freq != date_range_freq
            if create_new_date_ranges:
                new_date_ranges, new_date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                    startdate_obj=startdate_request, enddate_obj=ts_enddate, frequency=new_date_range_freq
                )
                logger.info(f"Updated request time-window for '{uuid}' from {date_range_freq} to {new_date_range_freq}")
                # continue with recursive call with updated (smaller or larger) time-window
                return cls._download_timeseries(
                    url=url,
                    date_ranges=new_date_ranges,
                    date_range_freq=new_date_range_freq,
                    ts_startdate=ts_startdate,
                    ts_enddate=ts_enddate,
                    retry_backoff_session=retry_backoff_session,
                    request_params=request_params,
                    pi_settings=pi_settings,
                    request_settings=request_settings,
                    drop_missing_values=drop_missing_values,
                    flag_threshold=flag_threshold,
                )
            else:
                DateFrequencyBuilder.log_progress_download_ts(
                    uuid=uuid, ts_startdate=ts_startdate, ts_enddate=ts_enddate, request_enddate=enddate_request
                )
                # ready to download timeseries (with new_date_range_freq)
                request_params["onlyHeaders"] = False
                request_params["showStatistics"] = False
                response = retry_backoff_session.get(url=url, params=request_params, verify=pi_settings.ssl_verify)

                # parse the response
                if response.ok:
                    pi_time_series = response.json()
                    time_series_set = TimeSeriesSet.from_pi_time_series(
                        pi_time_serie=pi_time_series,
                        drop_missing_values=drop_missing_values,
                        flag_threshold=flag_threshold,
                    )
                    if time_series_set.is_empty:
                        logger.debug(f"FEWS WebService request passing empty set: {response.url}")
                else:
                    logger.error(f"FEWS WebService request {response.url} responds {response.text}")
                    time_series_set = TimeSeriesSet()

                return time_series_set
