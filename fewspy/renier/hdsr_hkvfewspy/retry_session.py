from gapfinder import exceptions
from gapfinder.constants.webservices import PiWebServiceSettingsBase
from gapfinder.constants.webservices import ProductionWebServiceSettings
from gapfinder.constants.webservices import StandAloneWebServiceSettings
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from time import sleep
from typing import List
from typing import Tuple

import logging
import pandas as pd
import requests


logger = logging.getLogger(__name__)


class RequestsRetrySession:
    """
    Class that provides backoff/retry strategy for requests. Why?
    - We need to be tolerant for network failures: set retry + backoff_factor
    - We want to avoid this app to hang: set timeout
    Moreover, this class provides helpful debugging traces

    Example:
        settings = StandAloneWebServiceSettings()
        requests_retry_session = RequestsRetrySession(settings=settings)
        response = requests_retry_session.get(url='https://www.hdsr.nl')

    backoff_factor [seconds] allows you to change how long the processes will sleep between failed requests.
    The algorithm is as follows: {backoff factor} * (2 ** ({number of total retries} - 1))
    For example, if the backoff factor is set to:
        1 second: the successive sleeps will be 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256.
        2 seconds: the successive sleeps will be 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
        10 seconds: the successive sleeps will be 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560

    status_force_list:
    A set of integer HTTP status codes that we should force a retry on. A retry is initiated if the
    request method is in allowed_methods and the response status code is in status_forcelist.

    method_whitelist:
    A list with HTTP methods that we allow
    We use GET, as we not POST, PUT, PATCH, and DELETE vdSat API

    timeout_seconds:
    How long to wait for the server to send data before giving up? This arg is here and in can be defined on
    on a per-request basis (self.get(url=x, timeout_seconds=y)
    """

    retries: int = 2
    backoff_factor: float = 0.3
    status_force_list: Tuple = (500, 502, 504)
    allowed_methods: List[str] = ["HEAD", "GET", "OPTIONS"]  # we do not PUT/PATCH to PiWebService
    timeout_seconds: int = 2

    def __init__(self, settings: PiWebServiceSettingsBase):
        self.settings = settings
        self.datetime_previous_request = pd.Timestamp.now()  # this immutable object is updated during runtime
        self.__retry_session = None

    def _optional_sleep_until_next_request(self, time_since_previous_request: pd.Timedelta) -> None:
        """Ensure a minimum time between each PiWebService request."""
        logger.debug(f"time_since_previous_request {time_since_previous_request}")
        if time_since_previous_request > self.settings.min_time_between_requests:
            return
        timedelta_to_wait = self.settings.min_time_between_requests - time_since_previous_request
        seconds_to_wait = timedelta_to_wait.round(pd.Timedelta(seconds=1)).seconds  # noqa
        logger.debug(f"sleep {seconds_to_wait} seconds until next request")
        sleep(seconds_to_wait)

    def get(self, url: str, timeout_seconds: int = timeout_seconds, **kwargs) -> requests.Response:
        assert url.endswith("/"), f"url {url} must end with '/"
        now = pd.Timestamp.now()
        time_since_previous_request = now - self.datetime_previous_request
        self._optional_sleep_until_next_request(time_since_previous_request=time_since_previous_request)  # noqa
        self.datetime_previous_request = pd.Timestamp.now()
        try:
            response = self._retry_session.get(url=url, timeout=timeout_seconds, **kwargs)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
            logger.error(f"request failed for url: {url}, err: {err}")
            if isinstance(self.settings, StandAloneWebServiceSettings):
                msg = (
                    f"Please make sure fews SA webservice is running (D:/Tomcat/bin/Tomcat9w.exe). Verify with "
                    f"in browser url={self.settings.test_url}"
                )
                raise exceptions.StandAloneFewsWebServiceNotRunningError(message=msg, errors=err)
            assert isinstance(self.settings, ProductionWebServiceSettings)
            raise
        except Exception as err:
            logger.error(f"unexpected error: request failed for url={url}, err={err}")
            raise
        response_seconds = (pd.Timestamp.now() - now).seconds
        if response_seconds > self.settings.max_response_time.seconds:
            logger.warning(f"response_seconds={response_seconds}, status={response.status_code}, url={url}")
        return response

    @property
    def _retry_session(self) -> requests.Session:
        if self.__retry_session is not None:
            return self.__retry_session
        retry = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            method_whitelist=self.allowed_methods,  # method_whitelist deprecated in Retry v2.0, use allowed_methods=
            status_forcelist=self.status_force_list,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        self.__retry_session = session
        return self.__retry_session
