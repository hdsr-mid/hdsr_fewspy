from fewspy.constants import github
from fewspy.constants.paths import MAINTAINER_EMAIL
from fewspy.exceptions import NoPermissionInHdsrFewspyAuthError
from fewspy.exceptions import UserInvalidTokenHdsrFewspyAuthError
from fewspy.exceptions import UserNotFoundInHdsrFewspyAuthError
from fewspy.secrets import Secrets
from hdsr_pygithub import GithubFileDownloader
from typing import Dict
from typing import List

import logging
import pandas as pd
import validators


logger = logging.getLogger(__name__)


class Permissions:
    def __init__(self):
        self.secrets = Secrets()
        logger.info(
            "using hdsr_fewspy_email and hdsr_fewspy_token from os environmental variables (loaded from G:/secrets.env)"
        )
        self.hdsr_fewspy_email = self.validate_email(email=self.secrets.hdsr_fewspy_email)
        self.hdsr_fewspy_token = self.secrets.hdsr_fewspy_token.strip()
        self._permission_row = None
        self.ensure_any_permissions()

    @classmethod
    def validate_email(cls, email: str) -> str:
        logger.info("validatng email")
        assert isinstance(email, str) and email
        if not validators.email(value=email) == True:  # noqa
            raise AssertionError(f"email '{email}' is invalid")
        return email.strip()

    def ensure_any_permissions(self) -> None:
        if self.permissions_row.empty:
            raise NoPermissionInHdsrFewspyAuthError(message=f"user {self.hdsr_fewspy_email} has no permissions at all")

    @property
    def permissions_row(self) -> pd.Series:
        if self._permission_row is not None:
            return self._permission_row
        logger.info("determine permissions")
        github_downloader = GithubFileDownloader(
            target_file=github.GITHUB_HDSR_FEWSPY_AUTH_TARGET_FILE,
            allowed_period_no_updates=github.GITHUB_HDSR_FEWSPY_AUTH_ALLOWED_PERIOD_NO_UPDATES,
            repo_name=github.GITHUB_HDSR_FEWSPY_AUTH_REPO_NAME,
            branch_name=github.GITHUB_HDSR_FEWSPY_AUTH_BRANCH_NAME,
            repo_organisation=github.GITHUB_ORGANISATION,
        )
        df = pd.read_csv(filepath_or_buffer=github_downloader.get_download_url(), sep=";")

        # strip all values
        df_obj = df.select_dtypes(["object"])
        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

        # get row with matching email
        permissions_row = df[df["email"] == self.hdsr_fewspy_email]
        assert len(permissions_row) == 1, "code error"
        permissions_row = permissions_row.loc[0]

        # check user exists
        if permissions_row.empty:
            raise UserNotFoundInHdsrFewspyAuthError(
                f"email {self.hdsr_fewspy_email} not in permission file. Please contact {MAINTAINER_EMAIL}"
            )

        # check user has valid token
        if permissions_row["hdsr_fewspy_token"] != self.hdsr_fewspy_token:
            raise UserInvalidTokenHdsrFewspyAuthError(
                f"email found in permission file, but token does not match. Please contact {MAINTAINER_EMAIL}"
            )

        # hide token
        permissions_row["hdsr_fewspy_token"] = "..."
        self._permission_row = permissions_row
        return self._permission_row

    @staticmethod
    def split_string_in_list(value: str) -> List[str]:
        return [x for x in value.split(",") if x]

    @property
    def allowed_domain(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row["allowed_domain"])

    @property
    def allowed_service(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row["allowed_service"])

    @property
    def allowed_module_instance_id(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row["allowed_module_instance_id"])

    @property
    def allowed_filter_id(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row["allowed_filter_id"])

    @property
    def all_fields(self) -> Dict:
        return {
            "allowed_domain": self.allowed_domain,
            "allowed_service": self.allowed_service,
            "allowed_module_instance_id": self.allowed_module_instance_id,
            "allowed_filter_id": self.allowed_filter_id,
        }
