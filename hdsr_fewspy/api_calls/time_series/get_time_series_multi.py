from hdsr_fewspy.api_calls.time_series.base import GetTimeSeriesBase
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.date_frequency import DateFrequencyBuilder
from pathlib import Path
from typing import Dict
from typing import List

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class GetTimeSeriesMulti(GetTimeSeriesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_constructor()

    def validate_constructor(self):
        assert isinstance(self.location_ids, list) and self.location_ids
        assert [isinstance(x, str) for x in self.location_ids]

        assert isinstance(self.parameter_ids, list) and self.parameter_ids
        assert [isinstance(x, str) for x in self.parameter_ids]

        if self.qualifier_ids:
            assert isinstance(self.qualifier_ids, list) and self.qualifier_ids
            assert [isinstance(x, str) for x in self.qualifier_ids]

        any_multi = any([len(x) > 1 for x in (self.location_ids, self.parameter_ids, self.qualifier_ids) if x])
        assert (
            any_multi
        ), "Please specify >1 location_ids and/or parameter_ids and/or qualifier_ids. Or use get_time_series_single"

        if self.output_choice != OutputChoices.csv_file_in_download_dir:
            logger.warning(f"flag_threshold is not used for output_choice {self.output_choice}")
            if self.drop_missing_values == True:  # noqa
                logger.warning(f"drop_missing_values is not used for output_choice {self.output_choice}")

    @property
    def allowed_output_choices(self) -> List[str]:
        return [
            OutputChoices.xml_file_in_download_dir,
            OutputChoices.json_file_in_download_dir,
            OutputChoices.csv_file_in_download_dir,
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
            )
            file_name_keys = ["locationIds", "parameterIds", "qualifierIds", "startTime", "endTime"]
            file_name_values = [request_params.get(param, None) for param in file_name_keys]
            file_paths_created = self.response_manager.run(
                responses=responses,
                file_name_values=file_name_values,
                drop_missing_values=self.drop_missing_values,
                flag_threshold=self.flag_threshold,
            )
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
