from datetime import datetime
from fewspy.constants.choices import PiRestDocumentFormatChoices
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.time_series import TimeSeriesSet
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.date_frequency import DateFrequencyBuilder
from fewspy.utils.transformations import parameters_to_fews
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeseries:
    @classmethod
    def get_time_series(
        cls,
        url: str,
        pi_settings: PiSettings,
        request_settings: RequestSettings,
        retry_backoff_session: RequestsRetrySession,
        start_time: datetime,
        end_time: datetime,
        location_ids: Union[str, List[str]] = None,
        parameter_ids: Union[str, List[str]] = None,
        qualifier_ids: Union[str, List[str]] = None,
        thinning: int = None,
        only_headers: bool = False,
        show_statistics: bool = False,
        omit_empty_timeseries: bool = True,
        #
        drop_missing_values: bool = False,
        flag_threshold: int = 6,
        #
        to_csv: bool = True,
    ) -> List[TimeSeriesSet]:
        """Get FEWS qualifiers as a pandas DataFrame.
        Args:
            - url (str): url Delft-FEWS PI REST WebService.
              e.g. http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/qualifiers
            - start_time (datetime.datetime): datetime-object with start datetime to use in request.
            - end_time (datetime.datetime): datetime-object with end datetime to use in request.
            - location_ids (list): list with FEWS location ids to extract timeseries from. Defaults to None.
            - parameter_ids (list): list with FEWS parameter ids to extract timeseries from. Defaults to None.
            - qualifier_ids (list): list with FEWS qualifier ids to extract timeseries from. Defaults to None.
            - thinning (int): integer value for thinning parameter to use in request. Defaults to None.
            - only_headers (bool): if True, only headers will be returned. Defaults to False.
            - show_statistics (bool): if True, time series statistics will be included in header. Defaults to False.
            - omit_empty_timeseries (bool): if True, missing values (-999) are left out in response. Defaults to True
            - drop_missing_values (bool): Defaults to False.
            - flag_threshold (int): Exclude unreliable values. Default to 6 (only values with flag<6 will be included).
            - too_csv (bool): Write timeseries to output csv
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".

        """
        if only_headers or show_statistics:
            raise NotImplementedError

        if pi_settings.document_format != PiRestDocumentFormatChoices.json.value:
            raise NotImplementedError

        parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_settings)
        cartesian_parameters_list = cls._get_cartesian_parameters_list(parameters=parameters)
        timeseries_sets = [0] * len(cartesian_parameters_list)
        for index, request_params in enumerate(cartesian_parameters_list):
            ts_startdate = pd.Timestamp(request_params["startTime"])
            ts_enddate = pd.Timestamp(request_params["endTime"])
            date_ranges, date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                startdate_obj=ts_startdate,
                enddate_obj=ts_enddate,
                frequency=request_settings.default_request_period,
            )
            ts = cls._download_timeseries(
                url=url,
                date_ranges=date_ranges,
                date_range_freq=date_range_freq,
                ts_startdate=ts_startdate,
                ts_enddate=ts_enddate,
                retry_backoff_session=retry_backoff_session,
                request_params=request_params,
                pi_settings=pi_settings,
                request_settings=request_settings,
                drop_missing_values=drop_missing_values,
                flag_threshold=flag_threshold,
            )
            try:
                timeseries_sets[index] = ts
            except IndexError:
                timeseries_sets.append(ts)
        return timeseries_sets

    @classmethod
    def _get_nr_timestamps(cls, retry_backoff_session, url, params, pi_settings: PiSettings) -> int:
        params["onlyHeaders"] = True
        params["showStatistics"] = True
        response = retry_backoff_session.get(url=url, params=params, verify=pi_settings.ssl_verify)
        if not response.ok:
            raise AssertionError(f"reponse not okay, status_code={response.status_code}, err={response.text}")
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
                f"moduleInstanceIds = '{pi_settings.module_instance_ids}'. "
                f"Please specify 1 moduleInstanceIds in pi_settings."
            )
        raise AssertionError(msg)

    @classmethod
    def _download_timeseries(
        cls,
        url: str,
        date_ranges: List[Tuple[pd.Timestamp, pd.Timestamp]],
        date_range_freq: pd.Timedelta,
        ts_startdate: pd.Timestamp,
        ts_enddate: pd.Timestamp,
        retry_backoff_session: RequestsRetrySession,
        request_params: Dict,
        pi_settings: PiSettings,
        request_settings: RequestSettings,
        drop_missing_values: bool,
        flag_threshold: int,
    ) -> TimeSeriesSet:
        for request_index, (startdate_request, enddate_request) in enumerate(date_ranges):
            request_params["startTime"] = datetime_to_fews_str(startdate_request)
            request_params["endTime"] = datetime_to_fews_str(enddate_request)
            uuid = f"{request_params['locationIds'][0]} {request_params['parameterIds'][0]}"
            nr_timestamps_in_response = cls._get_nr_timestamps(
                retry_backoff_session=retry_backoff_session,
                url=url,
                params=request_params,
                pi_settings=pi_settings,
            )
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

    @classmethod
    def _get_cartesian_parameters_list(cls, parameters: Dict) -> List[Dict]:
        """Create all possible combinations of locationIds, parameterIds, and qualifierIds.

        Example input parameters = {
            'startTime': '2005-01-01T00:00:00Z',
            'endTime': '2023-01-01T00:00:00Z',
            'locationIds': ['KW215712', 'KW322613'],
            'parameterIds': ['Q.B.y', 'DD.y'],
            'onlyHeaders': False,
            'showStatistics': False,
            'documentVersion': 1.25,
            'documentFormat': 'PI_JSON',
            'filterId': 'INTERAL-API'
        }

        Go from
            {'locationIds': ['KW215712', 'KW322613'], 'parameterIds': ['Q.B.y', 'DD.y']}
        to [
            {'locationIds': 'KW215712', 'parameterIds': 'Q.B.y'},
            {'locationIds': 'KW215712', 'parameterIds': 'DD.y'},
            {'locationIds': 'KW322613', 'parameterIds': 'Q.B.y'},
            {'locationIds': 'KW322613', 'parameterIds': 'DD.y'},
        ]
        """
        location_ids = parameters.get("locationIds", [])
        parameter_ids = parameters.get("parameterIds", [])
        qualifier_ids = parameters.get("qualifierIds", [])
        cartesian_needed = max([len(x) for x in (location_ids, parameter_ids, qualifier_ids)]) > 1
        if not cartesian_needed:
            return [parameters]

        skip = "skip"
        request_args = []
        result = []
        for location_id in location_ids if location_ids else [skip]:
            for parameter_id in parameter_ids if parameter_ids else [skip]:
                for qualifier_id in qualifier_ids if qualifier_ids else [skip]:
                    request_arguments = {}
                    if location_id != skip:
                        request_arguments["locationIds"] = location_id
                    if parameter_id != skip:
                        request_arguments["parameterIds"] = parameter_id
                    if qualifier_id != skip:
                        request_arguments["qualifierIds"] = qualifier_id
                    uuid = list(request_arguments.values())
                    if uuid in request_args:
                        continue
                    parameters_copy = parameters.copy()
                    for k, v in request_arguments.items():
                        parameters_copy[k] = v
                    result.append(parameters_copy)
        return result
