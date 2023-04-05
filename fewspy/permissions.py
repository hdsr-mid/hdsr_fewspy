from fewspy.constants import github
from fewspy.exceptions import NoPermissionInHdsrFewspyAuthError
from fewspy.exceptions import UserNotFoundInHdsrFewspyAuthError
from hdsr_pygithub import GithubFileDownloader
from typing import Dict
from typing import List

import pandas as pd
import validators


class Permissions:
    def __init__(self, email: str, hdsr_fewspy_token: str):
        self.email = self.validate_email(email=email)
        self.hdsr_fewspy_token = hdsr_fewspy_token.strip()
        self._permission_row = None
        self.ensure_any_permissions()

    @classmethod
    def validate_email(cls, email: str) -> str:
        assert isinstance(email, str) and email
        if not validators.email(value=email) == True:  # noqa
            raise AssertionError(f"email '{email}' is invalid")
        return email.strip()

    def ensure_any_permissions(self) -> None:
        if self.permissions_row.empty:
            raise NoPermissionInHdsrFewspyAuthError(message=f"user {self.email} has no permissions at all")

    @property
    def permissions_row(self) -> pd.Series:
        if self._permission_row is not None:
            return self._permission_row
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
        permissions_row = df[(df["email"] == self.email) & (df["hdsr_fewspy_token"] == self.hdsr_fewspy_token)]
        if permissions_row.empty:
            raise UserNotFoundInHdsrFewspyAuthError(
                f"email {self.email}, hdsr_fewspy_token={self.hdsr_fewspy_token} not in permission file"
            )
        assert len(permissions_row) == 1, "code error"
        permissions_row = permissions_row.loc[0]
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
