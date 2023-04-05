from datetime import datetime
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.time_series import TimeSeriesSet
from fewspy.utils.date_frequency import DateFrequencyBuilder
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews
from typing import Dict
from typing import List
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
    ) -> TimeSeriesSet:
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
        Returns:
            df (pandas.DataFrame): Pandas dataframe with index "id" and columns "name" and "group_id".

        """
        report_string = "Headers {status}" if only_headers else "TimeSeries {status}"
        timeseriessets = []

        # do the request
        timer = Timer()
        parameters = parameters_to_fews(parameters=locals(), pi_settings=pi_settings)

        if only_headers or show_statistics:
            # TODO: implement this
            raise NotImplementedError

        date_freq_builder = DateFrequencyBuilder(request_settings=request_settings)

        cartesian_parameters_list = cls.get_cartesian_parameters_list(parameters=parameters)
        for request_params in cartesian_parameters_list:

            request_date_ranges, date_range_freq = date_freq_builder.create_date_ranges(
                startdate_obj=request_params["startTime"],
                enddate_obj=request_params["endTime"],
                frequency=request_settings.default_request_period,
            )

            for request_index, (startdate_request, enddate_request) in enumerate(request_date_ranges):
                nr_timestamps_in_response = cls._get_nr_timestamps(
                    retry_backoff_session=retry_backoff_session,
                    url=url,
                    params=request_params,
                    verify=pi_settings.ssl_verify,
                )
                logger.debug(f"nr_timestamps_in_response={nr_timestamps_in_response}")
                new_date_range_freq = date_freq_builder.optional_change_date_range_freq(
                    nr_timestamps=nr_timestamps_in_response, date_range_freq=date_range_freq
                )

                if new_date_range_freq != date_range_freq:

                    new_date_ranges, new_date_range_freq = date_freq_builder.create_date_ranges(
                        startdate_obj=request_params["startTime"],
                        enddate_obj=request_params["endTime"],
                        frequency=new_date_range_freq,
                    )
                    logger.info(f"updated request time-window from {date_range_freq} to {new_date_range_freq}")

                    raise NotImplementedError(
                        "renier hier was je gebleven: funcie/methode van boven zodat je recursive trick kan doen"
                    )
                    # TODO
                    # continue with recursive call with updated (smaller or larger) time-window
                    return self._add_ts_to_ts_analyser(
                        uuid=uuid,
                        int_loc=int_loc,
                        int_par=int_par,
                        ts_analyser=ts_analyser,
                        request_date_ranges=new_date_ranges,
                        date_range_freq=new_date_range_freq,
                        xml_start=xml_start,
                        xml_end_max_today=xml_end_max_today,
                    )
                else:
                    self._log_progress_download_ts(
                        uuid=uuid, xml_start=xml_start, xml_end_max_today=xml_end_max_today, request_end=enddate_request
                    )
                    df_ts = self.pi_rest.get_time_series_hdsr(
                        int_loc=int_loc,
                        int_par=int_par,
                        start=startdate_request,
                        end=enddate_request,
                    )
                    ts_analyser.add_df_time_series(df_ts=df_ts)

            date_range_tuples, frequency_used = DateFrequencyBuilder.create_date_ranges(
                startdate_obj, enddate_obj, frequency=request_settings.default_request_period
            )

            response = retry_backoff_session.get(url=url, params=parameters, verify=pi_settings.ssl_verify)
            timer.report(message=report_string.format(status="request"))

            # parse the response
            if response.ok:
                pi_time_series = response.json()
                time_series_set = TimeSeriesSet.from_pi_time_series(
                    pi_time_serie=pi_time_series,
                    drop_missing_values=drop_missing_values,
                    flag_threshold=flag_threshold,
                )
                timer.report(message=report_string.format(status="parsed"))
                if time_series_set.is_empty:
                    logger.debug(f"FEWS WebService request passing empty set: {response.url}")
            else:
                logger.error(f"FEWS WebService request {response.url} responds {response.text}")
                time_series_set = TimeSeriesSet()

        return time_series_set

    @classmethod
    def _get_nr_timestamps(cls, retry_backoff_session, url, params, verify) -> int:
        params["onlyHeaders"] = True
        params["showStatistics"] = True
        response = retry_backoff_session.get(url=url, params=params, verify=verify)
        if not response.ok:
            # TODO: fix this
            #  url
            #  'http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/timeseries/'
            #  params
            #  {'startTime': '2022-05-01T00:00:00Z', 'endTime': '2022-05-02T00:00:00Z', 'locationIds': ['OW433001'], 'parameterIds': ['H.G.0'], 'onlyHeaders': True, 'showStatistics': True, 'documentVersion': 1.25, 'documentFormat': 'PI_JSON', 'filterId': 'INTERAL-API'}
            #  verify
            #  True
            #  response.text = 'Filter INTERAL-API is not a valid child of root filter INTERNAL-API! Please check the filters.'
            raise NotImplementedError
        timeseries = response.json().get("timeSeries", None)
        if not timeseries:
            return 0

        if len(timeseries) > 1:
            assert (
                "moduleInstanceIds" in params
            ), f"No or multiple moduleInstanceIds results in multiple timeseries which is not implemented in hdsr_fewspy. Please specify 1 in pi_settings."
            raise AssertionError("code error multiple timeseries in _get_nr_timestamps")
        nr_timestamps = sum([int(x["header"]["valueCount"]) for x in timeseries])
        return nr_timestamps

    @classmethod
    def get_cartesian_parameters_list(cls, parameters: Dict) -> List[Dict]:
        """
        Go from
            {'locationIds': ['KW215712', 'KW322613'], 'parameterIds': ['Q.B.y', 'DD.y']}
        to [
            {'locationIds': 'KW215712', 'parameterIds': 'Q.B.y'},
            {'locationIds': 'KW215712', 'parameterIds': 'DD.y'},
            {'locationIds': 'KW322613', 'parameterIds': 'Q.B.y'},
            {'locationIds': 'KW322613', 'parameterIds': 'DD.y'},
        ]

        Example:
            input:
                parameters = {
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
            returns:
            [
                {
                    'documentFormat': 'PI_JSON',
                    'documentVersion': 1.25,
                    'endTime': '2023-01-01T00:00:00Z',
                    'filterId': 'INTERAL-API',
                    'locationIds': 'KW215712',
                    'onlyHeaders': False,
                    'parameterIds': 'Q.B.y',
                    'showStatistics': False,
                    'startTime': '2005-01-01T00:00:00Z'
                },
                {
                    'documentFormat': 'PI_JSON',
                    'documentVersion': 1.25,
                    'endTime': '2023-01-01T00:00:00Z',
                    'filterId': 'INTERAL-API',
                    'locationIds': 'KW215712',
                    'onlyHeaders': False,
                    'parameterIds': 'DD.y',
                    'showStatistics': False,
                    'startTime': '2005-01-01T00:00:00Z'
                },
                {
                    'documentFormat': 'PI_JSON',
                    'documentVersion': 1.25,
                    'endTime': '2023-01-01T00:00:00Z',
                    'filterId': 'INTERAL-API',
                    'locationIds': 'KW322613',
                    'onlyHeaders': False,
                    'parameterIds': 'Q.B.y',
                    'showStatistics': False,
                    'startTime': '2005-01-01T00:00:00Z'
                },
                {
                    'documentFormat': 'PI_JSON',
                    'documentVersion': 1.25,
                    'endTime': '2023-01-01T00:00:00Z',
                    'filterId': 'INTERAL-API',
                    'locationIds': 'KW322613',
                    'onlyHeaders': False,
                    'parameterIds': 'DD.y',
                    'showStatistics': False,
                    'startTime': '2005-01-01T00:00:00Z'
                }
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

    @classmethod
    def get_time_series_value_count(cls, int_loc: str, int_par: str, start: pd.Timestamp, end: pd.Timestamp) -> int:
        logger.debug("get_time_series_value_count")
        query_parameters_dict = self._update_default_query_parameters(
            int_loc=int_loc, int_par=int_par, start=start, end=end
        )
        query_parameters_dict["onlyHeaders"] = True
        query_parameters_dict["showStatistics"] = True
        time_series_url = f"{cls.settings.base_url}timeseries/"
        response = cls.retry_session.get(url=time_series_url, params=query_parameters_dict)
        if response.status_code != 200:
            raise exceptions.TsDownloadError(message=response.text)
        try:
            ts_reader = TimeSeriesReader(response_text=response.text)
            value_count = ts_reader.read_timeseries_response_value_count()
            return value_count
        except Exception as err:
            raise exceptions.TsReadError(message=err)
