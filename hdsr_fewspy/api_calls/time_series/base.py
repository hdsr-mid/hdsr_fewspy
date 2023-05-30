from abc import abstractmethod
from datetime import datetime
from hdsr_fewspy import exceptions
from hdsr_fewspy.api_calls.base import GetRequest
from hdsr_fewspy.constants.choices import ApiParameters
from hdsr_fewspy.constants.choices import PiRestDocumentFormatChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.converters.utils import datetime_to_fews_date_str
from hdsr_fewspy.converters.utils import fews_date_str_to_datetime
from hdsr_fewspy.converters.xml_to_python_obj import parse
from hdsr_fewspy.date_frequency import DateFrequencyBuilder
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesBase(GetRequest):
    response_text_no_ts_found = "No timeSeries found"
    response_text_location_not_found = "Some of the location ids do not exist"
    response_text_parameter_not_found = "Some of the parameters do not exists"

    start_time_all = datetime_to_fews_date_str(date_time=datetime(year=2011, month=1, day=1))
    end_time_all = datetime_to_fews_date_str(date_time=datetime.now())

    def __init__(
        self,
        start_time: Union[datetime, str],
        end_time: Union[datetime, str],
        location_ids: Union[List[str], str],
        parameter_ids: Union[List[str], str],
        qualifier_ids: Union[List[str], str] = None,
        thinning: int = None,
        omit_empty_time_series: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
        *args,
        **kwargs,
    ):
        self.start_time: datetime = self.__validate_time(time=start_time)
        self.end_time: datetime = self.__validate_time(time=end_time)
        self.location_ids = location_ids
        self.parameter_ids = parameter_ids
        self.qualifier_ids = qualifier_ids
        self.thinning = thinning
        self.omit_empty_time_series = omit_empty_time_series
        self.drop_missing_values = drop_missing_values
        self.flag_threshold = flag_threshold
        #
        self.__validate_constructor_base()
        super().__init__(*args, **kwargs)

    def __validate_constructor_base(self):
        assert self.start_time < self.end_time, f"start_time {self.start_time} must be before end_time {self.end_time}"

    @staticmethod
    def __validate_time(time: Union[datetime, str]) -> datetime:
        datetime_obj = fews_date_str_to_datetime(fews_date_str=time) if isinstance(time, str) else time
        return datetime_obj

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
            ApiParameters.omit_empty_time_series,
            ApiParameters.only_headers,
            ApiParameters.parameter_ids,
            ApiParameters.qualifier_ids,
            ApiParameters.show_attributes,
            ApiParameters.show_statistics,
            ApiParameters.start_time,
            ApiParameters.thinning,
        ]

    @property
    def required_request_args(self) -> List[str]:
        return [
            ApiParameters.document_format,
            ApiParameters.document_version,
            ApiParameters.end_time,
            ApiParameters.filter_id,
            ApiParameters.location_ids,
            ApiParameters.module_instance_ids,
            ApiParameters.parameter_ids,
            ApiParameters.start_time,
        ]

    @staticmethod
    def get_task_uuid(request_params: Dict) -> str:
        loc = request_params.get("locationIds", "")
        par = request_params.get("parameterIds", "")
        qual = request_params.get("qualifierIds", "")
        task_uuid = f"{loc} {par} {qual}"
        return task_uuid.strip()

    def _download_time_series(
        self,
        date_ranges: List[Tuple[pd.Timestamp, pd.Timestamp]],
        date_range_freq: pd.Timedelta,
        request_params: Dict,
        responses: Optional[List[ResponseType]] = None,
    ) -> List[ResponseType]:
        """Download time-series in little chunks by updating parameters 'startTime' and 'endTime' every loop.

        Before each download of actual time-series we first check nr_timestamps_in_response (a small request with
        showHeaders=True, and showStatistics=True). If that number if outside a certain bandwidth, then we update
        (smaller or larger windows) parameters 'startTime' and 'endTime' again.
        """
        responses = responses if responses else []

        # firstly, check if any time-series exist at all (no start_time and end_time)
        try:
            has_time_series = self._get_nr_timestamps_no_start_end(request_params=request_params) > 0
            if not has_time_series:
                task_uuid = self.get_task_uuid(request_params=request_params)
                logger.info(f"skipping since no time-series at all for '{task_uuid}'")
                return []
        except (exceptions.LocationIdsDoesNotExistErr, exceptions.ParameterIdsDoesNotExistErr) as err:
            logger.warning(err)
            return []

        # secondly, download time-series in little chunks
        for request_index, (data_range_start, data_range_end) in enumerate(date_ranges):
            # update start and end in request params
            request_params["startTime"] = datetime_to_fews_date_str(data_range_start)
            request_params["endTime"] = datetime_to_fews_date_str(data_range_end)
            try:
                nr_timestamps_in_response = self._get_nr_timestamps(request_params=request_params)
            except (exceptions.LocationIdsDoesNotExistErr, exceptions.ParameterIdsDoesNotExistErr) as err:
                logger.warning(err)
                return []
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
                self.request_settings.updated_request_period = new_date_range_freq
                new_date_ranges, new_date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                    startdate_obj=data_range_start,
                    enddate_obj=pd.Timestamp(self.end_time),
                    frequency=new_date_range_freq,
                )
                logger.debug(f"Updated request time-window from {date_range_freq} to {new_date_range_freq}")
                # continue with recursive call with updated (smaller or larger) time-window
                return self._download_time_series(
                    date_ranges=new_date_ranges,
                    date_range_freq=new_date_range_freq,
                    request_params=request_params,
                    responses=responses,
                )
            else:
                # ready to download time-series (with new_date_range_freq)
                request_params["onlyHeaders"] = False
                request_params["showStatistics"] = False
                response = self.retry_backoff_session.get(
                    url=self.url, params=request_params, verify=self.pi_settings.ssl_verify
                )
                if response.status_code != 200:
                    logger.error(f"FEWS Server responds {response.text}")
                else:
                    responses.append(response)
                DateFrequencyBuilder.log_progress_download_ts(
                    task=self.get_task_uuid(request_params=request_params),
                    request_end=data_range_end,
                    ts_start=pd.Timestamp(self.start_time),
                    ts_end=pd.Timestamp(self.end_time),
                )
        return responses

    def _get_statistics(self, request_params: Dict) -> ResponseType:
        request_params["onlyHeaders"] = True
        request_params["showStatistics"] = True
        response = self.retry_backoff_session.get(
            url=self.url, params=request_params, verify=self.pi_settings.ssl_verify
        )
        return response

    def _get_nr_timestamps_no_start_end(self, request_params: Dict) -> int:
        assert "moduleInstanceIds" in request_params, "code error _get_nr_timestamps_no_start_end"
        request_params_copy = request_params.copy()
        request_params_copy["startTime"] = self.start_time_all
        request_params_copy["endTime"] = self.end_time_all
        return self._get_nr_timestamps(request_params_copy)

    def _get_nr_timestamps(self, request_params: Dict) -> int:
        assert "moduleInstanceIds" in request_params, "code error _get_nr_timestamps"
        response = self._get_statistics(request_params=request_params)
        msg = f"status_code={response.status_code}, err={response.text}, request_params={request_params}"
        if not response.ok:
            return self.__get_nr_timestamps_invalid_response(response=response, msg=msg)
        if self.pi_settings.document_format == PiRestDocumentFormatChoices.json:
            time_series = response.json().get("timeSeries", None)
            if not time_series:
                return 0
            nr_time_series = len(time_series)
            if nr_time_series == 1:
                nr_timestamps = int(time_series[0]["header"]["valueCount"])
                return nr_timestamps
            msg = f"code error: found {nr_time_series} time_series in _get_nr_timestamps. Expected 0 or 1, {msg}"
            raise AssertionError(msg)
        elif self.pi_settings.document_format == PiRestDocumentFormatChoices.xml:
            xml_python_obj = parse(response.text)
            try:
                nr_timestamps = int(xml_python_obj.TimeSeries.series.header.valueCount.cdata)
                return nr_timestamps
            except Exception as err:
                raise AssertionError(f"could not get nr_timestamps from xml_python_obj, err={err}, {msg}")
        else:
            raise NotImplementedError(f"invalid document_format {self.pi_settings.document_format}")

    def __get_nr_timestamps_invalid_response(self, response: ResponseType, msg: str):
        if self.response_text_no_ts_found in response.text:
            return 0
        if self.response_text_location_not_found in response.text:
            raise exceptions.LocationIdsDoesNotExistErr(msg)
        elif self.response_text_parameter_not_found in response.text:
            raise exceptions.ParameterIdsDoesNotExistErr(msg)
        raise AssertionError(f"(unknown non-200 response, {msg}")

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError
