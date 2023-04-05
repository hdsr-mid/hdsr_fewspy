from fewspy.constants.paths import HDSR_FEWSPY_VERSION
from fewspy.constants.pi_settings import PiSettings
from fewspy.permissions import Permissions
from functools import wraps
from time import perf_counter
from typing import Dict

import logging
import platform
import tracemalloc


logger = logging.getLogger(__name__)


def create_bug_report_when_error(func):
    """Create a bug report in terminal logging."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        runtime_data = {}
        tracemalloc.start()
        start_time = perf_counter()
        try:
            func(*args, **kwargs)
        except Exception as err:
            current, peak = tracemalloc.get_traced_memory()
            finish_time = perf_counter()
            tracemalloc.stop()
            #
            runtime_data["function"] = func.__name__
            runtime_data["memory_usage"] = f"{current / 10**6:.6f} MB"
            runtime_data["memory_usage_peak"] = f"{peak / 10**6:.6f} MB"
            runtime_data["time elapsed [seconds]"] = f"{finish_time - start_time:.6f}"
            runtime_data["hdsr_fewspy_version"] = HDSR_FEWSPY_VERSION
            runtime_data["platform"] = platform.platform()  # e.g. 'Linux-3.3.0-8.fc16.x86_64-x86_64-with-...'
            #
            error = f"{type(err)}: {err}"
            _pi_settings = args[0].pi_settings
            _permissions = args[0].permissions
            _parameters = kwargs
            #
            bug_report = BugReport(
                error=error,
                pi_settings=_pi_settings,
                permissions=_permissions,
                parameters=_parameters,
                runtime_data=runtime_data,
            )
            bug_report.create_report_in_terminal()
            bug_report.shutdown()

    return wrapper


class BugReport:
    def __init__(
        self, error: str, pi_settings: PiSettings, permissions: Permissions, parameters: Dict, runtime_data: Dict
    ):
        self.message = error
        self.pi_settings: PiSettings = pi_settings
        self.permissions = permissions
        self.parameters: dict = parameters
        self.runtime_data: dict = runtime_data

    @staticmethod
    def shutdown():
        exit(1)

    def create_report_in_terminal(self) -> None:
        short_dashed_line = f"{'-'*20}"
        long_dashed_line = f"{'-'*40}"

        print(long_dashed_line)
        print(short_dashed_line)
        print("error")
        print(short_dashed_line)
        print(self.message)

        mapper = {
            "pi_settings": self.pi_settings.all_fields,
            "parameters": self.parameters,
            "runtime data": self.runtime_data,
            "permissions": self.permissions.all_fields,
        }

        for k, v in mapper.items():
            print(short_dashed_line)
            print(k)
            print(short_dashed_line)
            for _k, _v in v.items():
                print(f"{_k}={_v}")

        print(long_dashed_line)
