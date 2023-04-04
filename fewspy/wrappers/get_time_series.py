from datetime import datetime
from fewspy.constants.pi_settings import PiSettings
from fewspy.retry_session import RequestsRetrySession
from fewspy.time_series import TimeSeriesSet
from fewspy.utils.timer import Timer
from fewspy.utils.transformations import parameters_to_fews
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import itertools
import logging
import pandas as pd


logger = logging.getLogger(__name__)


class DateFrequency:
    @staticmethod
    def _create_date_ranges(
        startdate_obj: pd.Timestamp,
        enddate_obj: pd.Timestamp,
        frequency: pd.Timedelta,
    ) -> Tuple[List[Tuple[pd.Timestamp, pd.Timestamp]], pd.Timedelta]:
        """
        Example:
            startdate_obj = pd.Timestamp("2010-04-27 00:00:00")
            enddate_obj = pd.Timestamp("2010-04-27 05:00:00")
            frequency = pd.Timedelta(hours=1, seconds=1f0, milliseconds=100)
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


class GetTimeseries:
    @classmethod
    def get_time_series(
        cls,
        url: str,
        pi_settings: PiSettings,
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

        cartesian_parameters_list = cls.get_cartesian_parameters_list(
            parameters=parameters, location_ids=location_ids, parameter_ids=parameter_ids, qualifier_ids=qualifier_ids
        )
        for cartesian_parameters in cartesian_parameters_list:
            nr_timestamps = cls._get_nr_timestamps(
                retry_backoff_session=retry_backoff_session, url=url, params=cartesian_parameters, verify=ssl_verify
            )
            response = retry_backoff_session.get(url=url, params=parameters, verify=ssl_verify)
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
        timeseries = response.json()["timeSeries"]
        if len(timeseries) > 1:
            logger.debug(f"get_timeseries with parameters {params} results in {len(timeseries)} timeseries")
        nr_timestamps = sum([int(x["header"]["valueCount"]) for x in timeseries])

        if len(timeseries) != 1:
            # TODO: implement this
            #  params = {
            #     "documentFormat": "PI_JSON",
            #     "filterId": "INTERNAL-API",
            #     "startTime": "2005-01-01T00:00:00Z",
            #     "endTime": "2023-01-01T00:00:00Z",
            #     "locationIds": "KW215712",
            #     "parameterIds": "DD.y",
            #     "onlyHeaders": True,
            #     "showStatistics": True,
            #  }
            #  results in len(timeseries) == 3
            #  timeseries = [
            #     {
            #         "header": {
            #             "type": "instantaneous",
            #             "moduleInstanceId": "ImportOpvlWater",
            #             "locationId": "KW215712",
            #             "parameterId": "DD.y",
            #             "timeStep": {"unit": "nonequidistant"},
            #             "startDate": {"date": "2004-12-31", "time": "23:00:00"},
            #             "endDate": {"date": "2023-12-31", "time": "23:00:00"},
            #             "missVal": "-999.0",
            #             "stationName": "HARMELERWAARD_2157-K_HARMELERWAARD-pompvijzel1_afvoer",
            #             "lat": "52.088590381584716",
            #             "lon": "4.980657829604588",
            #             "x": "127137.0",
            #             "y": "455670.0",
            #             "z": "0.0",
            #             "units": "s",
            #             "firstValueTime": {"date": "2005-12-31", "time": "23:00:00"},
            #             "lastValueTime": {"date": "2022-12-31", "time": "23:00:00"},
            #             "maxValue": "4826096",
            #             "minValue": "43739",
            #             "valueCount": "18",
            #         }
            #     },
            #     {
            #         "header": {
            #             "type": "instantaneous",
            #             "moduleInstanceId": "WerkFilter",
            #             "locationId": "KW215712",
            #             "parameterId": "DD.y",
            #             "timeStep": {"unit": "nonequidistant"},
            #             "startDate": {"date": "2004-12-31", "time": "23:00:00"},
            #             "endDate": {"date": "2023-12-31", "time": "23:00:00"},
            #             "missVal": "-999.0",
            #             "stationName": "HARMELERWAARD_2157-K_HARMELERWAARD-pompvijzel1_afvoer",
            #             "lat": "52.088590381584716",
            #             "lon": "4.980657829604588",
            #             "x": "127137.0",
            #             "y": "455670.0",
            #             "z": "0.0",
            #             "units": "s",
            #             "firstValueTime": {"date": "2005-12-31", "time": "23:00:00"},
            #             "lastValueTime": {"date": "2022-12-31", "time": "23:00:00"},
            #             "maxValue": "4826096",
            #             "minValue": "43739",
            #             "valueCount": "18",
            #         }
            #     },
            #     {
            #         "header": {
            #             "type": "instantaneous",
            #             "moduleInstanceId": "MetingenFilter",
            #             "locationId": "KW215712",
            #             "parameterId": "DD.y",
            #             "timeStep": {"unit": "nonequidistant"},
            #             "startDate": {"date": "2004-12-31", "time": "23:00:00"},
            #             "endDate": {"date": "2023-12-31", "time": "23:00:00"},
            #             "missVal": "-999.0",
            #             "stationName": "HARMELERWAARD_2157-K_HARMELERWAARD-pompvijzel1_afvoer",
            #             "lat": "52.088590381584716",
            #             "lon": "4.980657829604588",
            #             "x": "127137.0",
            #             "y": "455670.0",
            #             "z": "0.0",
            #             "units": "s",
            #             "firstValueTime": {"date": "2021-12-31", "time": "23:00:00"},
            #             "lastValueTime": {"date": "2022-12-31", "time": "23:00:00"},
            #             "maxValue": "83206",
            #             "minValue": "41542",
            #             "valueCount": "2",
            #         }
            #     },
            # ]
            raise NotImplementedError("this should not happen")

        return nr_timestamps

    @classmethod
    def get_cartesian_parameters_list(
        cls, parameters: Dict, location_ids: List[str], parameter_ids: List[str], qualifier_ids: List[str]
    ) -> List[Dict]:
        if not any([location_ids, parameter_ids, qualifier_ids]):
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
