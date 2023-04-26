from datetime import timedelta
from pathlib import Path


GITHUB_ORGANISATION = "hdsr-mid"
GITHUB_HDSR_FEWSPY_AUTH_REPO_NAME = "hdsr_fewspy_auth"
GITHUB_HDSR_FEWSPY_AUTH_BRANCH_NAME = "main"
GITHUB_HDSR_FEWSPY_AUTH_USERS_TARGET_FILE = Path("users.csv")
GITHUB_HDSR_FEWSPY_AUTH_SETTINGS_TARGET_FILE = Path("settings.csv")
GITHUB_HDSR_FEWSPY_AUTH_ALLOWED_PERIOD_NO_UPDATES = timedelta(weeks=52)
