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
    col_github_user = "github_user"
    col_allowed_domain = "allowed_domain"
    col_allowed_service = "allowed_service"
    col_allowed_module_instance_id = "allowed_module_instance_id"
    col_allowed_filter_id = "allowed_filter_id"
    all_cols = [
        col_github_user,
        col_allowed_domain,
        col_allowed_service,
        col_allowed_module_instance_id,
        col_allowed_filter_id,
    ]

    def __init__(self, secrets: Secrets):
        self.secrets = secrets
        self._permission_row = None
        self._github_downloader = None
        self._github_user_url = None
        self._ensure_has_permission()

    def _ensure_has_permission(self):
        assert isinstance(self.permissions_row, pd.Series) and not self.permissions_row.empty

    @property
    def github_downloader(self):
        if self._github_downloader is not None:
            return self._github_downloader
        self._github_downloader = GithubFileDownloader(
            target_file=github.GITHUB_HDSR_FEWSPY_AUTH_PERMISSIONS_TARGET_FILE,
            allowed_period_no_updates=github.GITHUB_HDSR_FEWSPY_AUTH_ALLOWED_PERIOD_NO_UPDATES,
            repo_name=github.GITHUB_HDSR_FEWSPY_AUTH_REPO_NAME,
            branch_name=github.GITHUB_HDSR_FEWSPY_AUTH_BRANCH_NAME,
            repo_organisation=github.GITHUB_ORGANISATION,
            personal_access_token=self.secrets.github_personal_access_token,
        )
        return self._github_downloader

    @property
    def permissions_row(self) -> pd.Series:
        if self._permission_row is not None:
            return self._permission_row
        logger.info("determine permissions")
        df = pd.read_csv(filepath_or_buffer=self.github_downloader.get_download_url(), sep=";")

        expected_cols = sorted(self.all_cols)
        found_cols = sorted(df.columns)
        if expected_cols != found_cols:
            msg = f"code error: found_cols {found_cols} while expected_cols {expected_cols} in repo hdsr_fewspy_auth"
            raise AssertionError(msg)

        # strip all values
        df_obj = df.select_dtypes(["object"])
        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

        # get row with matching github user
        msg_user = f"github_user {self.github_downloader.user_url}"
        permissions_row = df[df[self.col_github_user] == self.github_downloader.user_url]
        nr_rows = len(permissions_row)
        if nr_rows != 1:
            msg = f"{msg_user} is registered {nr_rows} times in repo hdsr_fewspy_auth"
            raise UserNotFoundInHdsrFewspyAuthError(msg)
        permissions_row = permissions_row.iloc[0]

        # check github user exists
        if permissions_row.empty:
            raise NoPermissionInHdsrFewspyAuthError(f"{msg_user} has no permissions in repo hdsr_fewspy_auth")

        self._permission_row = permissions_row
        return self._permission_row

    @staticmethod
    def split_string_in_list(value: str) -> List[str]:
        return [x for x in value.split(",") if x]

    @property
    def allowed_domain(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row[self.col_allowed_domain])

    @property
    def allowed_service(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row[self.col_allowed_service])

    @property
    def allowed_module_instance_id(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row[self.col_allowed_module_instance_id])

    @property
    def allowed_filter_id(self) -> List[str]:
        return self.split_string_in_list(value=self.permissions_row[self.col_allowed_filter_id])
