from hdsr_fewspy.constants import github
from hdsr_fewspy.exceptions import NoPermissionInHdsrFewspyAuthError
from hdsr_fewspy.exceptions import UserNotFoundInHdsrFewspyAuthError
from hdsr_fewspy.secrets import Secrets
from hdsr_pygithub import GithubFileDownloader
from typing import List

import logging
import pandas as pd


logger = logging.getLogger(__name__)


class Permissions:
    def __init__(self, secrets: Secrets):
        self.secrets = secrets
        self._permission_row = None

    @property
    def permissions_row(self) -> pd.Series:
        if self._permission_row is not None:
            return self._permission_row
        logger.info("determine permissions")
        github_downloader = GithubFileDownloader(
            target_file=github.GITHUB_HDSR_FEWSPY_AUTH_USERS_TARGET_FILE,
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
        permissions_row = df[df["email"] == self.secrets.github_email]
        nr_rows = len(permissions_row)
        if nr_rows != 1:
            msg = f"github_email {self.secrets.github_email} is registered {nr_rows} times in hdsr_fewspy_auth"
            raise UserNotFoundInHdsrFewspyAuthError(msg)
        permissions_row = permissions_row.loc[0]

        # check github_email exists
        if permissions_row.empty:
            raise NoPermissionInHdsrFewspyAuthError(f"github_email {self.secrets.github_email} has no permissions")

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
