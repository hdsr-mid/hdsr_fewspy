from fewspy.api_calls.time_series.base import GetTimeSeriesBase
from fewspy.constants.choices import OutputChoices
from fewspy.utils.date_frequency import DateFrequencyBuilder
from pathlib import Path
from typing import Dict
from typing import List

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesMulti(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
        ]

    def run(self) -> List[Path]:
        all_file_paths = []
        cartesian_parameters_list = self._get_cartesian_parameters_list(parameters=self.initial_fews_parameters)
        for index, request_params in enumerate(cartesian_parameters_list):
            date_ranges, date_range_freq = DateFrequencyBuilder.create_date_ranges_and_frequency_used(
                startdate_obj=pd.Timestamp(self.start_time),
                enddate_obj=pd.Timestamp(self.end_time),
                frequency=self.request_settings.default_request_period,
            )
            responses = self._download_timeseries(
                date_ranges=date_ranges,
                date_range_freq=date_range_freq,
                request_params=request_params,
                drop_missing_values=self.drop_missing_values,
                flag_threshold=self.flag_threshold,
            )
            params = ["locationIds", "parameterIds", "qualifierIds", "startTime", "endTime"]
            file_name_values = [request_params.get(param) for param in params if request_params.get(param)]
            file_paths_created = self.response_handler.run(responses=responses, file_name_values=file_name_values)
            all_file_paths.extend(file_paths_created)
        logger.info(f"finished download and writing to {len(all_file_paths)} file(s)")
        return all_file_paths

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