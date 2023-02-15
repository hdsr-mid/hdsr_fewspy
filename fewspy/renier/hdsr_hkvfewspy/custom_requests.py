from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Tuple

import logging
import requests
import time


logger = logging.getLogger(__name__)


class RequestsRetrySession:
    """
    Class that provides backup/retry strategy for requests. Why?
    - We need to be tolerant for network failures: set retry + backoff_factor
    - We want to avoid this app to hang: set timeout
    Moreover, this class provides helpful debugging traces

    Example Usage 1:
    requests_retry_session = RequestsRetrySession()
    response = requests_retry_session.get(
        url='https://www.hdsr.nl'
        )

    Example Usage 2 (use timeout + create custom session):
    custom_session = requests.Session()
    custom_session.auth = ('user', 'pass')
    custom_session.headers.update({'x-test': 'true'})
    requests_retry_session = RequestsRetrySession()
    response = requests_retry_session.get(
        url='https://www.hdsr.nl',
        timeout=3,
        )
    """

    def __init__(self):
        """
        backoff_factor [seconds]:
        - 1 second? then successive request sleep will be --> 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256.
        - 2 seconds? --> 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
        - 10 seconds? --> 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560

        status_force_list:
        A set of integer HTTP status codes that we should force a retry on. A retry is initiated if the
        request method is in allowed_methods and the response status code is in status_forcelist.

        method_whitelist:
        A list with HTTP methods that we allow
        We use GET, as we not POST, PUT, PATCH, and DELETE vdSat API

        NOTE: timeout is not in this constructor as it is not something you set up in the session, but it's done
        on a per-request basis (in other words: in the get() method).
        """
        self.retries: int = 3
        self.backoff_factor: float = 0.3
        self.status_force_list: Tuple = (500, 502, 504)
        self.method_whitelist = ["HEAD", "GET", "OPTIONS"]

    def get(self, url: str, timeout: int = None, session: requests.Session = None, **kwargs) -> requests.Response:
        # Note: timeout unit is seconds
        session = session or requests.Session()
        now = time.time()
        requests_retry_session = self.__create_retry_session(session=session)
        try:
            response = requests_retry_session.get(url=url, timeout=timeout, **kwargs)
            seconds_elapsed = int(time.time() - now)
            msg = f"request worked after {seconds_elapsed} seconds, status: {response.status_code}, url: {url}"
            logger.debug(msg) if seconds_elapsed < 5 else logger.info(msg)
            return response
        except requests.exceptions.HTTPError as err:
            time_elapsed = time.time() - now
            logger.error(f"request failed after {time_elapsed} seconds, url: {url}, err: {err}")
            logging.error(f"could not log in to API. Probably wrong credentials, err:{err}")
        except Exception as err:
            time_elapsed = time.time() - now
            logger.error(f"request failed after {time_elapsed} seconds, url: {url}, err: {err}")
            raise

    def __create_retry_session(self, session: requests.Session) -> requests.Session:
        retry = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            method_whitelist=self.method_whitelist,
            status_forcelist=self.status_force_list,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
