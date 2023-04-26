from abc import abstractmethod
from hdsr_fewspy.constants.choices import ApiParameters
from hdsr_fewspy.constants.choices import OutputChoices
from hdsr_fewspy.constants.custom_types import ResponseType
from hdsr_fewspy.constants.pi_settings import PiSettings
from hdsr_fewspy.constants.request_settings import RequestSettings
from hdsr_fewspy.converters.manager import ResponseManager
from hdsr_fewspy.converters.utils import datetime_to_fews_str
from hdsr_fewspy.converters.utils import snake_to_camel_case
from hdsr_fewspy.retry_session import RetryBackoffSession
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


class GetRequest:
    def __init__(self, output_choice: str, retry_backoff_session: RetryBackoffSession):
        self.retry_backoff_session: RetryBackoffSession = retry_backoff_session
        self.pi_settings: PiSettings = retry_backoff_session.pi_settings
        self.request_settings: RequestSettings = retry_backoff_session.request_settings
        self.output_choice: str = self.validate_output_choice(output_choice=output_choice)
        self.output_dir: Optional[Path] = self.validate_output_dir(output_dir=retry_backoff_session.output_dir)
        self.url: str = f"{self.pi_settings.base_url}{self.url_post_fix}/"
        self.pi_settings.document_format = OutputChoices.get_pi_rest_document_format(output_choice)
        self._initial_fews_parameters = None
        self._filtered_fews_parameters = None
        self.response_manager = ResponseManager(
            output_choice=self.output_choice,
            request_class=self.__class__.__name__.lower(),
            output_dir=self.output_dir,
        )
        self.validate_base_constructor()

    @property
    @abstractmethod
    def url_post_fix(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def allowed_request_args(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def required_request_args(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def allowed_output_choices(self) -> List[str]:
        """Every GetRequest has its own list with >=1 hdsr_fewspy.constants.choices.OutputChoices."""
        raise NotImplementedError

    def validate_base_constructor(self):
        all_parameters = self._unpack_all_parameters()
        msg = "code error required_request_args"
        for x in self.required_request_args:
            if x not in self.allowed_request_args:
                raise AssertionError(f"{msg} {x} not in allowed {self.allowed_request_args}")
            if x not in all_parameters.keys():
                raise AssertionError(f"{msg} {x} not in all_parameters {all_parameters.keys()}")

    def validate_output_choice(self, output_choice: str) -> str:
        if output_choice in self.allowed_output_choices:
            return output_choice
        raise AssertionError(
            f"invalid output_choice '{output_choice}'. {self.__class__.__name__} has valid_output_choices "
            f"{self.allowed_output_choices}. See earlier logging why we use {self.__class__.__name__}."
        )

    def validate_output_dir(self, output_dir: Path) -> Path:
        if OutputChoices.needs_output_dir(output_choice=self.output_choice) and not isinstance(output_dir, Path):
            msg = f"output_choice {self.output_choice} requires an output_dir. Please specify Api output_directory_root"
            raise AssertionError(msg)
        return output_dir

    def _unpack_all_parameters(self) -> Dict:
        """
        Returns for example:
            {
                '_filtered_fews_parameters': None,
                '_initial_fews_parameters': None,
                 'default_request_period': Timedelta('35 days 00:00:00'),
                 'document_format': 'PI_JSON',
                 'document_version': 1.25,
                 'domain': 'localhost',
                 'filter_id': 'INTERNAL-API',
                 'max_request_nr_timestamps': 100000,
                 'max_request_period': Timedelta('728 days 00:00:00'),
                 'max_request_size_kb': 3000,
                 'max_response_time': Timedelta('0 days 00:00:20'),
                 'min_request_nr_timestamps': 10000,
                 'min_time_between_requests': Timedelta('0 days 00:00:01'),
                 'module_instance_ids': 'WerkFilter',
                 'output_choice': 'json_response_in_memory',
                 'output_dir': None,
                 'port': 8080,
                 'service': 'FewsWebServices',
                 'settings_name': 'default stand-alone',
                 'show_attributes': True,
                 'ssl_verify': True,
                 'time_zone': 'Etc/GMT-0',
                 'url': 'http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/parameters/'
            }
        """
        all_parameters = dict()
        for key, value in self.__dict__.items():
            if isinstance(value, RetryBackoffSession) or isinstance(value, ResponseManager):
                continue
            elif isinstance(value, PiSettings) or isinstance(value, RequestSettings):
                for k, v in value.__dict__.items():
                    all_parameters[k] = v
            else:
                all_parameters[key] = value
        return all_parameters

    @property
    def initial_fews_parameters(self) -> Dict:
        if self._initial_fews_parameters is not None:
            return self._initial_fews_parameters
        self._initial_fews_parameters = self._parameters_to_fews(
            parameters=self._unpack_all_parameters(), do_filter=False
        )
        return self._initial_fews_parameters

    @property
    def filtered_fews_parameters(self) -> Dict:
        if self._filtered_fews_parameters is not None:
            return self._filtered_fews_parameters
        self._filtered_fews_parameters = self._parameters_to_fews(
            parameters=self._unpack_all_parameters(), do_filter=True
        )
        return self._filtered_fews_parameters

    def _parameters_to_fews(self, parameters: Dict, do_filter: bool) -> Dict:
        """Prepare Python API dictionary for FEWS API request.

        Arg:
            - do_filter (bool): filters out all parameters not in allowed_request_args."""

        def _convert_kv(k: str, v) -> Tuple[str, Any]:
            if k in ApiParameters.non_pi_settings_keys_datetime():
                v = datetime_to_fews_str(v)
            k = snake_to_camel_case(k)
            return k, v

        # non pi settings
        filtered = self.allowed_request_args if do_filter else ApiParameters.non_pi_settings_keys()
        params_non_pi = [_convert_kv(k, v) for k, v in parameters.items() if k in filtered]

        # pi settings
        filtered = self.allowed_request_args if do_filter else ApiParameters.pi_settings_keys()
        params_pi = [_convert_kv(k, v) for k, v in self.pi_settings.all_fields.items() if k in filtered]

        fews_parameters = {x[0]: x[1] for x in params_non_pi + params_pi if x[1] is not None}
        return fews_parameters

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def handle_response(self, response: ResponseType, **kwargs):
        return self.response_manager.run(response=response, **kwargs)
