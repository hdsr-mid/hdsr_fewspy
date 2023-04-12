from abc import abstractmethod
from fewspy.constants.pi_settings import PiSettings
from fewspy.constants.request_settings import RequestSettings
from fewspy.retry_session import RetryBackoffSession


class GetRequest:
    def __init__(self, retry_backoff_session: RetryBackoffSession):
        self.retry_backoff_session: RetryBackoffSession = retry_backoff_session
        self.pi_settings: PiSettings = retry_backoff_session.pi_settings
        self.request_settings: RequestSettings = retry_backoff_session.request_settings
        self.url: str = f"{self.pi_settings.base_url}/{self.url_post_fix}/"

    @abstractmethod
    @property
    def url_post_fix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError
