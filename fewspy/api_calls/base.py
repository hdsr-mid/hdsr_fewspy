from abc import abstractmethod
from fewspy.constants.choices import ApiParameters
from fewspy.constants.choices import OutputChoices
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.response_converters.base import ResponseManager
from fewspy.retry_session import RetryBackoffSession
from fewspy.utils.conversions import datetime_to_fews_str
from fewspy.utils.conversions import snake_to_camel_case
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
        self._initial_fews_parameters = None
        self._filtered_fews_parameters = None

        self.response_handler = ResponseManager(
            output_choice=self.output_choice,
            request_method=self.url_post_fix.lower(),
            output_dir=self.output_dir,
        )

    @property
    @abstractmethod
    def url_post_fix(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def whitelist_request_args(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def valid_output_choices(self) -> List[OutputChoices]:
        raise NotImplementedError

    def validate_output_choice(self, output_choice: str) -> str:
        if output_choice in self.valid_output_choices:
            return output_choice
        raise AssertionError(
            f"invalid output_choice '{output_choice}'. {self.__class__.__name__} has valid_output_choices "
            f"{self.valid_output_choices}. See earlier logging why we use {self.__class__.__name__}."
        )

    def validate_output_dir(self, output_dir: Path) -> Path:
        if OutputChoices.needs_output_dir(output_choice=self.output_choice) and not isinstance(output_dir, Path):
            msg = f"output_choice {self.output_choice} requires an output_dir. Please specify Api output_directory_root"
            raise AssertionError(msg)
        return output_dir

    @property
    def initial_fews_parameters(self) -> Dict:
        if self._initial_fews_parameters is not None:
            return self._initial_fews_parameters
        self._initial_fews_parameters = self._parameters_to_fews(parameters=self.__dict__, do_filter=False)
        return self._initial_fews_parameters

    @property
    def filtered_fews_parameters(self) -> Dict:
        if self._filtered_fews_parameters is not None:
            return self._filtered_fews_parameters
        self._filtered_fews_parameters = self._parameters_to_fews(parameters=self.__dict__, do_filter=True)
        return self._filtered_fews_parameters

    def _parameters_to_fews(self, parameters: Dict, do_filter: bool) -> Dict:
        """Prepare Python API dictionary for FEWS API request.

        Arg:
            - do_filter (bool): filters out all parameters not in whitelist_request_args."""

        def _convert_kv(k: str, v) -> Tuple[str, Any]:
            if k in ApiParameters.non_pi_settings_keys_datetime():
                v = datetime_to_fews_str(v)
            elif k == "attributes":
                k = "show_attributes"
                v = True
            k = snake_to_camel_case(k)
            return k, v

        # non pi settings
        whitelist = self.whitelist_request_args if do_filter else ApiParameters.non_pi_settings_keys()
        params_non_pi = [_convert_kv(k, v) for k, v in parameters.items() if k in whitelist]

        # pi settings
        whitelist = self.whitelist_request_args if do_filter else ApiParameters.pi_settings_keys()
        params_pi = [_convert_kv(k, v) for k, v in self.pi_settings.all_fields.items() if k in whitelist]

        fews_parameters = {x[0]: x[1] for x in params_non_pi + params_pi if x[1] is not None}
        return fews_parameters

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def handle_response(self, response):
        return self.response_handler.run(response)
