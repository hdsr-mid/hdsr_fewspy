from dotenv import load_dotenv
from hdsr_fewspy.constants.paths import GITHUB_PERSONAL_ACCESS_TOKEN
from pathlib import Path
from typing import Union

import logging
import os


logger = logging.getLogger(__name__)


class Secrets:
    def __init__(self, github_personal_access_token: str = None, secrets_env_path: Union[str, Path] = None):
        self.secrets_env_path = Path(secrets_env_path)
        self._github_personal_access_token = github_personal_access_token
        self._validate_constructor(token=github_personal_access_token)

    def _validate_constructor(self, token: str = None):
        self._validate_token(token=token) if token else self._read_dotenv_only_once_into_os()

    @staticmethod
    def _validate_token(token: str) -> None:
        logger.info("validatng github_personal_access_token")
        # check 1
        if not isinstance(token, str) or len(token) < 10:
            msg = "invalid token. Please read 'Token' on 'https://pypi.org/project/hdsr-pygithub/' how to create one"
            raise AssertionError(msg)
        # check 2
        is_stripped = len(token) == len(token.strip())
        assert is_stripped, f"token '{token}' contains whitespace"

    def _read_dotenv_only_once_into_os(self):
        logger.info(f"loading token from '{self.secrets_env_path}' into os environmental variables")
        try:
            assert self.secrets_env_path.is_file(), f"could not find token_path '{self.secrets_env_path}'"
            load_dotenv(dotenv_path=self.secrets_env_path.as_posix())
        except Exception as err:
            raise AssertionError(f"could not load secrets_env_path '{self.secrets_env_path}', err={err}")

    @property
    def github_personal_access_token(self) -> str:
        if self._github_personal_access_token is not None:
            return self._github_personal_access_token
        key = GITHUB_PERSONAL_ACCESS_TOKEN
        token = os.environ.get(key, None)
        if not token:
            raise AssertionError(f"file '{self.secrets_env_path}' exists, but it must contain a row: {key}=blabla")
        self._validate_token(token=token)
        self._github_personal_access_token = token
        return self._github_personal_access_token
