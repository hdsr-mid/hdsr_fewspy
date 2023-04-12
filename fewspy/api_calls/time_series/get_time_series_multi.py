from datetime import datetime
from fewspy.api_calls.time_series.base import GetTimeSeriesBase
from fewspy.constants.choices import OutputChoices
from fewspy.utils.date_frequency import DateFrequencyBuilder
from typing import Dict
from typing import List

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesMulti(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def valid_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
        ]

    def run(self):
        cartesian_parameters_list = self._get_cartesian_parameters_list(parameters=self.initial_fews_parameters)
        for index, request_params in enumerate(cartesian_parameters_list):
            date_ranges, date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                startdate_obj=pd.Timestamp(self.start_time),
                enddate_obj=pd.Timestamp(self.end_time),
                frequency=self.request_settings.default_request_period,
            )
            response = self._download_timeseries(
                date_ranges=date_ranges,
                date_range_freq=date_range_freq,
                request_params=request_params,
                drop_missing_values=self.drop_missing_values,
                flag_threshold=self.flag_threshold,
            )
            raise NotImplementedError(
                "renier hier was je gebleven. Iets generieks maken voor reponse to csv?"
                "- ik wil geen overkill voor bijv timezoneid"
                "- ik wil niet in elke api_call Class 6 methodes maken: "
                "   - 'xml_file_in_download_dir', "
                "   - 'json_file_in_download_dir', "
                "   - 'csv_file_in_download_dir', "
                "   - 'xml_response_in_memory', "
                "   - 'json_response_in_memory', "
                "   - 'pandas_dataframe_in_memory'"
            )
            # assert self.do_save_to_output_dir, "code error"
            #
            # OutputChoices.
            # self.save_response_to_file(response=response)

            # # parse the response
            #                 if response.ok:
            #                     pi_time_series = response.json()
            #                     time_series_set = TimeSeriesSet.from_pi_time_series(
            #                         pi_time_serie=pi_time_series,
            #                         drop_missing_values=drop_missing_values,
            #                         flag_threshold=flag_threshold,
            #                     )
            #                     if time_series_set.is_empty:
            #                         logger.debug(f"FEWS WebService request passing empty set: {response.url}")
            #                 else:
            #                     logger.error(f"FEWS WebService request {response.url} responds {response.text}")
            #                     time_series_set = TimeSeriesSet()
            #
            #                 return time_series_set

            try:
                timeseries_sets[index] = ts  # noqa
            except IndexError:
                timeseries_sets.append(ts)  # noqa
        return timeseries_sets  # noqa

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
