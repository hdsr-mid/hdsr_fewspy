from collections import namedtuple
from datetime import datetime
from enum import Enum
from gapfinder import exceptions
from gapfinder.constants import paths_and_settings
from gapfinder.constants.webservices import ProductionWebServiceSettings
from gapfinder.constants.webservices import StandAloneWebServiceSettings
from gapfinder.hdsr_hkvfewspy.retry_session import RequestsRetrySession
from gapfinder.utils import get_class_attributes
from hkvfewspy.utils.untangle import Element
from hkvfewspy.utils.untangle import parse_raw
from typing import Dict
from typing import List

import hkvfewspy
import logging
import pandas as pd
import pytz
import re  # noqa
import requests


logger = logging.getLogger(__name__)

XmlColumnNamedTuple = namedtuple(typename="XmlColumn", field_names=["name", "must_exist", "skip"])
HkvPiRestType = hkvfewspy.io.rest_fewspi.PiRest  # noqa
HkvDataQueryType = hkvfewspy.utils.query_helper.DataQuery  # noqa


class PiRestDocumentFormatChoices(Enum):
    json = "PI_JSON"
    xml = "PI_XML"

    @classmethod
    def get_all(cls) -> List[str]:
        return [x.value for x in cls.__members__.values()]


class TimeZoneChoices(Enum):
    gmt = "Etc/GMT"
    gmt_0 = "Etc/GMT-0"
    eu_amsterdam = "Europe/Amsterdam"


class PiRestTimeSeriesHeaderChoices(Enum):
    longform = "longform"  # has one row per observation, with metadata recorded within the table as values.
    multiindex = "multiindex"  # try to parse the header into a single df where the header is contained as multi-index.
    # dictionary = "dict"  # NOT YET IMPLEMENTED: parse response events in a df and the header in a separate dictionary


class PiRestTimeSeriesFormatChoices(Enum):
    json = "json"  # returns JSON formatted output
    df = "df"  # returns a DataFrame
    gzip = "gzip"  # returns a Gzip compressed JSON string


class PiRestTimeSeriesAvoidThese(Enum):
    """getTimeSeries() with these queryParameters results in 'Invalid request. Unexpected parameter used'."""

    forecast_search_count = "forecastSearchCount"
    delete_all_modifiers = "deleteAllModifiers"
    show_location_attributes = "showLocationAttributes"
    version = "version"
    commit_modifiers = "commitModifiers"
    client_time_zone = "clientTimeZone"


class TimeSeriesCols:
    # meta columns
    moduleInstanceId = "moduleInstanceId"
    qualifierId = "qualifierId"
    parameterId = "parameterId"
    units = "units"
    locationId = "locationId"
    stationName = "stationName"
    latitude = "latitude"
    longitude = "longitude"
    # data columns
    date_time = "datetime"
    flag = "flag"
    value = "value"
    user = "user"

    @classmethod
    def get_all(cls) -> List[str]:
        return list(get_class_attributes(the_class=cls).values())

    @classmethod
    def get_meta_columns(cls) -> List[str]:
        return [x for x in cls.get_all() if x not in cls.__data_columns()]

    @classmethod
    def get_data_columns(cls) -> List[str]:
        return [x for x in cls.get_all() if x in cls.__data_columns()]

    @classmethod
    def __data_columns(cls) -> List[str]:
        return [cls.date_time, cls.flag, cls.value, cls.user]


class TimeSeriesReader:
    def __init__(
        self,
        response_text: str,
        meta_columns: List[str] = None,
        data_columns: List[str] = None,
        client_time_zone: TimeZoneChoices = TimeZoneChoices.gmt,
    ):
        self.meta_columns = meta_columns if meta_columns else TimeSeriesCols.get_meta_columns()
        self.data_columns = data_columns if data_columns else TimeSeriesCols.get_data_columns()
        self.client_time_zone = client_time_zone
        self.time_series_xml = parse_raw(xml=response_text)

    def read_timeseries_response_value_count(self) -> int:
        series = self.time_series_xml.TimeSeries.series
        nr_series = len(series)
        if nr_series > 1:
            module_instance_ids = [_series.header.moduleInstanceId.cdata for _series in series]
            raise AssertionError(
                f"settings error: expected one series in raw xml with 1 moduleInstanceId, but found {nr_series} "
                f"series with module_instance_ids={module_instance_ids}. Are you sure you defined one "
                f"module_instance_id (see self.settings.module_instance_id)?"
            )
        value_count = int(self.time_series_xml.TimeSeries.series.header.valueCount.cdata)
        return value_count

    def read_timeseries_response(self) -> pd.DataFrame:
        """Parse raw xml into panda dataframe. This is a look-a-like of
        hkvfewspy.utils.pi_helper.read_timeseries_response() but then: less code, better readable,
        and better logging.

        Example raw xml response:
        ------------------------
        <?xml version="1.0" encoding="UTF-8"?>
        <TimeSeries xmlns="http://www.wldelft.nl/fews/PI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews/PI http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd" version="1.25" xmlns:fs="http://www.wldelft.nl/fews/fs">  # noqa
            <timeZone>0.0</timeZone>
            <series>
                <header>
                    <type>instantaneous</type>
                    <moduleInstanceId>ImportOpvlWater</moduleInstanceId>
                    <locationId>KW100111</locationId>
                    <parameterId>F.0</parameterId>
                    <timeStep unit="nonequidistant"/>
                    <startDate date="2012-10-27" time="23:59:59"/>
                    <endDate date="2012-10-28" time="23:59:59"/>
                    <missVal>-999.0</missVal>
                    <stationName>WIJKERSLOOT_1001-K_WIJKERSLOOT-pompvijzel1_aanvoer</stationName>
                    <lat>51.975277004252774</lat>
                    <lon>5.321724723696098</lon>
                    <x>150501.0</x>
                    <y>442987.0</y>
                    <units>Hz</units>
                </header>
                <event date="2012-10-28" time="00:00:00" value="0" flag="0"/>
                <event date="2012-10-28" time="00:15:00" value="0" flag="0"/>
                <event date="2012-10-28" time="00:30:00" value="0" flag="0"/>
                <event date="2012-10-28" time="00:45:00" value="0" flag="0"/>
                <event date="2012-10-28" time="01:00:00" value="0" flag="0"/>
                <event date="2012-10-28" time="01:15:00" value="0" flag="0"/>
                ...
                <event date="2012-10-28" time="23:15:00" value="0" flag="0"/>
                <event date="2012-10-28" time="23:30:00" value="0" flag="0"/>
                <event date="2012-10-28" time="23:45:00" value="0" flag="0"/>
            </series>
        </TimeSeries>
        """
        data = {key: [] for key in self.meta_columns + self.data_columns}
        server_time_zone = self.__get_server_time_zone(time_series_xml=self.time_series_xml)
        client_time_zone = pytz.timezone(zone=self.client_time_zone.value)
        for series in self.time_series_xml.TimeSeries.series:
            data = self.__collect_meta_data(parameter=TimeSeriesCols.qualifierId, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.moduleInstanceId, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.locationId, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.latitude, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.longitude, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.stationName, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.parameterId, series=series, data=data)
            data = self.__collect_meta_data(parameter=TimeSeriesCols.units, series=series, data=data)
            data = self.__collect_data(
                data=data,
                series=series,
                client_time_zone=client_time_zone,
                server_time_zone=server_time_zone,
            )
            data = self.__ensure_dict_lists_same_length(data=data)
        df_time_series = self.__create_df_time_series(data=data)
        return df_time_series

    def __collect_meta_data(self, parameter: str, series, data: Dict) -> Dict:
        assert parameter in self.meta_columns, f"parameter {parameter} is not meta parameter"
        if parameter not in data:
            return data
        try:
            parameter_obj = getattr(series.header, parameter)
        except AttributeError as err:
            logger.debug(f"could not get parameter {parameter} from xml, err={err}")
            data[parameter].append("")
            return data
        parameter_data = parameter_obj.cdata
        data[parameter].append(parameter_data)
        return data

    def __collect_data(
        self,
        data: Dict,
        series: Element,
        client_time_zone: datetime.tzinfo,
        server_time_zone: datetime.tzinfo,
    ) -> Dict:
        if not hasattr(series, "event"):
            for data_column in self.data_columns:
                data[data_column].append(None)
            return data

        for data_column in self.data_columns:

            if data_column == TimeSeriesCols.date_time:
                dates = self.__get_dates(
                    series=series,
                    client_time_zone=client_time_zone,
                    server_time_zone=server_time_zone,
                )
                data[TimeSeriesCols.date_time].extend(dates)
                continue
            for event in series.event:
                try:
                    event_data = event[data_column]
                except AttributeError as err:
                    event_data = ""
                    logger.debug(f"could not get parameter {data_column} from xml, err={err}")
                data[data_column].extend([event_data])
        return data

    @staticmethod
    def __ensure_dict_lists_same_length(data: Dict) -> Dict:
        list_lengths = [len(data[column]) for column in data.keys()]
        min_len = min(list_lengths)
        max_len = max(list_lengths)

        no_data_found = min_len == max_len == 1
        if no_data_found:
            raise exceptions.NoTsExistsError(message=f"no data found, data={data}")
        if not all(x in (min_len, max_len) for x in list_lengths) and len(set(list_lengths)) == 2:
            raise AssertionError(f"length of data dict values (lists) must be either min {min_len} or max {max_len}")
        for column in data.keys():
            if len(data[column]) == max_len:
                continue
            last_value = data[column][-1]
            new_values = [last_value] * (max_len - min_len)
            data[column].extend(new_values)
        return data

    @staticmethod
    def __get_dates(
        series: Element,
        server_time_zone: datetime.tzinfo,
        client_time_zone: datetime.tzinfo,
    ) -> List:
        """
        from [{'date': '2012-10-28', 'time': '00:00:00'}, {'date': '2012-10-28', 'time': '00:15:00'}, ..]
        to [(2012, 10, 28, 0, 0, 0), (2012, 10, 28, 0, 15, 0), ..]
        """
        times = [
            (
                *map(int, re.split(pattern=r"-", string=event["date"])),
                *map(int, re.split(pattern=r":|\.", string=event["time"])),
            )
            for event in series.event
        ]
        # TODO: find out why hkv does this ("len(times[0]) == 7")?
        if len(times[0]) == 7:
            times = [item[:-1] + (item[-1] * 1000,) for item in times]
        server_times = [datetime(*times[x], tzinfo=server_time_zone) for x in range(len(times))]
        server_tz_equals_client_tz = server_times[0].astimezone(client_time_zone) == server_times[0]
        dates = server_times if server_tz_equals_client_tz else [x.astimezone(client_time_zone) for x in server_times]
        return dates

    @staticmethod
    def __create_df_time_series(data: Dict) -> pd.DataFrame:
        columns = list(data.keys())
        df_time_series = pd.DataFrame(columns=columns)
        for column in columns:
            df_time_series[column] = data[column]
        df_time_series.sort_values(by=columns, inplace=True)
        df_time_series.sort_index(inplace=True)
        return df_time_series

    @staticmethod
    def __get_server_time_zone(time_series_xml: Element) -> datetime.tzinfo:
        """Etc/GMT* follows POSIX standard, incl. counter-intuitive sign change (
        see https://stackoverflow.com/q/51542167/2459096)."""
        time_zone_value = int(float(time_series_xml.TimeSeries.timeZone.cdata))
        if time_zone_value >= 0:
            time_zone = "Etc/GMT-" + str(time_zone_value)
        else:
            time_zone = "Etc/GMT+" + str(time_zone_value)
        return pytz.timezone(zone=time_zone)


class HdsrPiRest:
    """
    We use hkvfewspy only to get default query_parameters (and example code). A lot of things are possible, but we
    miss: retry/backoff/timeout options when requesting webservice. And it is not possible to get ONLY the  nr of
    timestamps in a timeseries window (onlyHeaders=True + showStatistics=True) results in an error because of this
    bug: https://github.com/HKV-products-services/hkvfewspy/issues/20 (we are not waiting for hkv to fix the bug)
    """

    def __init__(
        self,
        use_stand_alone_webservice: bool = paths_and_settings.USE_STAND_ALONE_WEBSERVICE,
    ):
        self.use_stand_alone_webservice = use_stand_alone_webservice
        self.settings = StandAloneWebServiceSettings() if use_stand_alone_webservice else ProductionWebServiceSettings()
        self.retry_session = RequestsRetrySession(settings=self.settings)
        self.hkv_pi = self.__get_pi_rest_instance()
        self._default_query_parameters = None
        self.__validate_webservice_connection()

    def __validate_webservice_connection(self) -> None:
        assert self.settings.base_url.endswith("/")
        filters_url = f"{self.settings.base_url}filters/"
        response = self.retry_session.get(url=filters_url)
        if response.status_code == 200:
            return
        http_code_meaning = requests.status_codes._codes[response.status_code][0]  # noqa
        raise AssertionError(
            f"normal request (without hkvfewspy) for url {filters_url} resulted in code={response.status_code} "
            f"({http_code_meaning}), is_redirected={response.is_redirect}, text={response.text}"
        )

    def __get_pi_rest_instance(self) -> HkvPiRestType:
        pi_rest = hkvfewspy.Pi(protocol=self.settings.protocol)
        pi_rest.setUrl(url=self.settings.base_url)
        assert pi_rest.documentFormat == PiRestDocumentFormatChoices.json.value  # default documentFormat is JSON
        assert pi_rest.documentVersion == self.settings.document_version == "1.25"
        return pi_rest

    def _get_default_query_parameters(self) -> Dict:
        """hkvfewspy methods accept both HkvDataQueryType and dictionary
        data_query = HkvDataQueryType -> getTimeseries(queryParameters=data_query, ..)
        data_query.query = dictionary -> getTimeseries(queryParameters=data_query.query, ..)
        """
        data_query = self.hkv_pi.setQueryParameters(prefill_defaults=True, protocol=self.settings.protocol)
        # edit default 1: defaults work for rest protocol when we update useDisplayUnits to False
        data_query.useDisplayUnits(value=False)
        if self.settings.module_instance_id:
            # edit default 2: we retrieve data from specific moduleInstanceId
            data_query.moduleInstanceIds(value=[self.settings.module_instance_id])
        return data_query.query

    def _update_default_query_parameters(
        self, int_loc: str, int_par: str, start: pd.Timestamp, end: pd.Timestamp
    ) -> Dict:
        query_parameters = self._get_default_query_parameters()
        query_parameters["locationIds"] = [int_loc]
        query_parameters["parameterIds"] = [int_par]
        query_parameters["startTime"] = start.isoformat(sep="T") + "Z"
        query_parameters["endTime"] = end.isoformat(sep="T") + "Z"
        return query_parameters

    def get_time_series_hkv(self, int_loc: str, int_par: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        query_parameters = self._update_default_query_parameters(int_loc=int_loc, int_par=int_par, start=start, end=end)
        df_hkv = self.hkv_pi.getTimeSeries(
            queryParameters=query_parameters,
            header=PiRestTimeSeriesHeaderChoices.longform.value,
            setFormat=PiRestTimeSeriesFormatChoices.df.value,
            print_response=False,
            tz=TimeZoneChoices.gmt.value,
        )
        return df_hkv

    def get_time_series_hdsr(self, int_loc: str, int_par: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        logger.debug("get_time_series_hdsr")
        query_parameters = self._update_default_query_parameters(int_loc=int_loc, int_par=int_par, start=start, end=end)
        time_series_url = f"{self.settings.base_url}timeseries/"
        response = self.retry_session.get(url=time_series_url, params=query_parameters)
        if response.status_code != 200:
            raise exceptions.TsDownloadError(message=response.text)
        try:
            ts_reader = TimeSeriesReader(response_text=response.text)
            df_ts = ts_reader.read_timeseries_response()
        except exceptions.NoTsExistsError:
            raise
        except Exception as err:
            raise exceptions.TsReadError(message=err)
        return df_ts

    def get_time_series_value_count(self, int_loc: str, int_par: str, start: pd.Timestamp, end: pd.Timestamp) -> int:
        logger.debug("get_time_series_value_count")
        query_parameters_dict = self._update_default_query_parameters(
            int_loc=int_loc, int_par=int_par, start=start, end=end
        )
        query_parameters_dict["onlyHeaders"] = True
        query_parameters_dict["showStatistics"] = True
        time_series_url = f"{self.settings.base_url}timeseries/"
        response = self.retry_session.get(url=time_series_url, params=query_parameters_dict)
        if response.status_code != 200:
            raise exceptions.TsDownloadError(message=response.text)
        try:
            ts_reader = TimeSeriesReader(response_text=response.text)
            value_count = ts_reader.read_timeseries_response_value_count()
            return value_count
        except Exception as err:
            raise exceptions.TsReadError(message=err)
