from dotenv import load_dotenv
from fewspy.constants.paths import GITHUB_PERSONAL_ACCESS_TOKEN
from fewspy.constants.paths import HDSR_FEWSPY_EMAIL
from fewspy.constants.paths import HDSR_FEWSPY_TOKEN
from fewspy.constants.paths import SECRETS_ENV_PATH
from pathlib import Path

import logging
import os


logger = logging.getLogger(__name__)


class Secrets:
    def __init__(self, secrets_env_path: Path = SECRETS_ENV_PATH):
        self.secrets_env_path = secrets_env_path
        self._personal_access_token = None
        self._hdsr_fewspy_email = None
        self._hdsr_fewspy_token = None
        self._read_dotenv_only_once_into_os()

    def _read_dotenv_only_once_into_os(self):
        token_path = self.secrets_env_path
        logger.info(f"loading secrets from '{self.secrets_env_path} into os environmental variables")
        try:
            assert token_path.is_file(), f"could not find {token_path}"
            load_dotenv(dotenv_path=token_path.as_posix())
        except Exception as err:
            raise AssertionError(f"could not load envs from {self.secrets_env_path}, err={err}")

    @property
    def personal_access_token(self) -> str:
        if self._personal_access_token is not None:
            return self._personal_access_token
        key = GITHUB_PERSONAL_ACCESS_TOKEN
        try:
            token = os.environ.get(key, None)
            assert token, f"file {self.secrets_env_path} exists, but it must contain a row: {key}=blabla"
            assert isinstance(token, str) and len(token) > 20, f"{key} must a string of at least 20 chars"
            self._personal_access_token = token
        except Exception as err:
            msg = (
                f"could not get {key} from {self.secrets_env_path}. err={err}. Please read "
                f"topic 'Token' on https://pypi.org/project/hdsr-pygithub/"
            )
            raise AssertionError(msg)
        return self._personal_access_token

    @property
    def hdsr_fewspy_email(self) -> str:
        if self._hdsr_fewspy_email is not None:
            return self._hdsr_fewspy_email
        key = HDSR_FEWSPY_EMAIL
        try:
            hdsr_fewspy_email = os.environ.get(key, None)
            assert hdsr_fewspy_email, f"file {self.secrets_env_path} exists, but it must contain a row: {key}=blabla"
            assert (
                isinstance(hdsr_fewspy_email, str) and len(hdsr_fewspy_email) > 10
            ), f"{key} must a string of at least 10 chars"
            self._hdsr_fewspy_email = hdsr_fewspy_email
        except Exception as err:
            raise AssertionError(f"could not get {key} from {self.secrets_env_path}. err={err}")
        return self._hdsr_fewspy_email

    @property
    def hdsr_fewspy_token(self) -> str:
        if self._hdsr_fewspy_token is not None:
            return self._hdsr_fewspy_token
        key = HDSR_FEWSPY_TOKEN
        try:
            hdsr_fewspy_token = os.environ.get(key, None)
            assert hdsr_fewspy_token, f"file {self.secrets_env_path} exists, but it must contain a row: {key}=blabla"
            assert (
                isinstance(hdsr_fewspy_token, str) and len(hdsr_fewspy_token) > 10
            ), f"{key} must a string of at least 10 chars"
            self._hdsr_fewspy_token = hdsr_fewspy_token
        except Exception as err:
            raise AssertionError(f"could not get {key} from {self.secrets_env_path}. err={err}")
        return self._hdsr_fewspy_token
