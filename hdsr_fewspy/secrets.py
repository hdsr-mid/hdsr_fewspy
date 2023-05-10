from dotenv import load_dotenv
from hdsr_fewspy.constants.paths import GITHUB_EMAIL
from hdsr_fewspy.constants.paths import GITHUB_PERSONAL_ACCESS_TOKEN
from pathlib import Path
from typing import Union

import logging
import os
import validators


logger = logging.getLogger(__name__)


class Secrets:
    def __init__(
        self,
        github_email: str = None,
        github_personal_access_token: str = None,
        secrets_env_path: Union[str, Path] = None,
    ):
        self.secrets_env_path = Path(secrets_env_path)
        self._github_email = github_email
        self._github_personal_access_token = github_personal_access_token
        self._validate_constructor(email=github_email, token=github_personal_access_token)

    def _validate_constructor(self, email: str, token: str):
        if email:
            self._validate_email(email=email)
        if token:
            self._validate_token(token=token)
        env_must_exist = not email or not token
        if env_must_exist:
            msg = "loading secrets from .env file as empty argument(s) github_email and/or github_personal_access_token"
            logger.info(msg)
            self._read_dotenv_only_once_into_os()

    @staticmethod
    def _validate_email(email: str) -> None:
        logger.info("validating github_email")
        # check 1
        assert isinstance(email, str) and len(email) > 5, f"email '{email}' must be str of at least 5 chars"
        # check 2
        is_stripped = len(email) == len(email.strip())
        assert is_stripped, f"email '{email}' contains whitespace"
        # check 3
        if not validators.email(value=email) == True:  # noqa
            raise AssertionError(f"email '{email}' is invalid")

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
        token_path = self.secrets_env_path
        logger.info(f"loading secrets from '{self.secrets_env_path} into os environmental variables")
        try:
            assert token_path.is_file(), f"could not find token_path '{token_path}'"
            load_dotenv(dotenv_path=token_path.as_posix())
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

    @property
    def github_email(self) -> str:
        if self._github_email is not None:
            return self._github_email
        key = GITHUB_EMAIL
        email = os.environ.get(key, None)
        if not email:
            raise AssertionError(f"file '{self.secrets_env_path}' exists, but it must contain a row: {key}=blabla")
        self._validate_email(email=email)
        self._github_email = email
        return self._github_email
