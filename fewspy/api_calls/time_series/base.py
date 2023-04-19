from abc import abstractmethod
from datetime import datetime
from fewspy.api_calls.base import GetRequest
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import PiRestDocumentFormatChoices
from fewspy.response_converters.xml_to_python_obj import parse
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.date_frequency import DateFrequencyBuilder
from typing import Dict
from typing import List
from typing import Tuple

import logging
import pandas as pd
import requests


logger = logging.getLogger(__name__)


class GetTimeSeriesBase(GetRequest):
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
        *args,
        **kwargs,
    ):
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

    @property
    def url_post_fix(self):
        return "timeseries"

    @property
    def allowed_request_args(self) -> List[str]:
        return [
            ApiParameters.document_format,
            ApiParameters.document_version,
            ApiParameters.end_time,
            ApiParameters.filter_id,
            ApiParameters.include_location_relations,
            ApiParameters.location_ids,
            ApiParameters.module_instance_ids,
            ApiParameters.omit_empty_timeseries,
            ApiParameters.only_headers,
            ApiParameters.parameter_ids,
            ApiParameters.qualifier_ids,
            ApiParameters.show_attributes,
            ApiParameters.show_statistics,
            ApiParameters.start_time,
            ApiParameters.thinning,
        ]

    def _download_timeseries(
        self,
        date_ranges: List[Tuple[pd.Timestamp, pd.Timestamp]],
        date_range_freq: pd.Timedelta,
        request_params: Dict,
        drop_missing_values: bool,
        flag_threshold: int,
    ) -> List[requests.models.Response]:
        """Download timeseries in little chunks by updating parameters 'startTime' and 'endTime' every loop.

        Before each download of actual timeseries we first check nr_timestamps_in_response (a small request with
        showStatistics=True, and showStatistics=True). If that number if outside a certain bandwith, then we update
        (smaller or larger windows) parameters 'startTime' and 'endTime' again.
        """
        responses = []
        for request_index, (data_range_start, data_range_end) in enumerate(date_ranges):
            # update start and end in request params
            request_params["startTime"] = datetime_to_fews_str(data_range_start)
            request_params["endTime"] = datetime_to_fews_str(data_range_end)
            nr_timestamps_in_response = self._get_nr_timestamps(params=request_params)
            logger.debug(f"nr_timestamps_in_response={nr_timestamps_in_response}")
            new_date_range_freq = DateFrequencyBuilder.optional_change_date_range_freq(
                nr_timestamps=nr_timestamps_in_response,
                date_range_freq=date_range_freq,
                request_settings=self.request_settings,
                startdate_request=data_range_start,
                enddate_request=data_range_end,
            )
            create_new_date_ranges = new_date_range_freq != date_range_freq
            if create_new_date_ranges:
                new_date_ranges, new_date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                    startdate_obj=data_range_start,
                    enddate_obj=pd.Timestamp(self.end_time),
                    frequency=new_date_range_freq,
                )
                logger.info(f"Updated request time-window from {date_range_freq} to {new_date_range_freq}")
                # continue with recursive call with updated (smaller or larger) time-window
                return self._download_timeseries(
                    date_ranges=new_date_ranges,
                    date_range_freq=new_date_range_freq,
                    request_params=request_params,
                    drop_missing_values=drop_missing_values,
                    flag_threshold=flag_threshold,
                )
            else:
                DateFrequencyBuilder.log_progress_download_ts(
                    data_range_start=data_range_start,
                    data_range_end=data_range_end,
                    ts_end=pd.Timestamp(self.end_time),
                )
                # ready to download timeseries (with new_date_range_freq)
                request_params["onlyHeaders"] = False
                request_params["showStatistics"] = False
                response = self.retry_backoff_session.get(
                    url=self.url, params=request_params, verify=self.pi_settings.ssl_verify
                )
                if response.status_code != 200:
                    logger.error(f"FEWS Server responds {response.text}")
                responses.append(response)
        return responses

    def _get_nr_timestamps(self, params: Dict) -> int:
        params["onlyHeaders"] = True
        params["showStatistics"] = True
        response = self.retry_backoff_session.get(url=self.url, params=params, verify=self.pi_settings.ssl_verify)
        if not response.ok:
            raise AssertionError(f"response not okay, status_code={response.status_code}, err={response.text}")
        if self.pi_settings.document_format == PiRestDocumentFormatChoices.json:
            timeseries = response.json().get("timeSeries", None)
            if not timeseries:
                return 0
            if len(timeseries) == 1:
                nr_timestamps = int(timeseries[0]["header"]["valueCount"])
                return nr_timestamps
            # error since too many timeseries
            msg = "Found multiple timeseries in _get_nr_timestamps"
            if "moduleInstanceIds" not in params:
                msg += f"Please specify 1 moduleInstanceIds in pi_settings instead of '{self.pi_settings.module_instance_ids}'"
            raise AssertionError(msg)
        elif self.pi_settings.document_format == PiRestDocumentFormatChoices.xml:
            xml_python_obj = parse(response.text)
            try:
                nr_timestamps = int(xml_python_obj.TimeSeries.series.header.valueCount.cdata)
                return nr_timestamps
            except Exception as err:
                raise AssertionError(f"could not get nr_timestamps from xml_python_obj, err={err}")
        else:
            raise NotImplementedError("only xml and json are available")

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError
