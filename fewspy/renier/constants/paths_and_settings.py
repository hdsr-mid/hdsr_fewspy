from datetime import timedelta
from pathlib import Path

import pandas as pd


USE_STAND_ALONE_WEBSERVICE = True


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_SOCKET_TIMEOUT = None
REDIS_GAP_START_END_FMT = "%Y%m%d_%H%M%S"
SAVE_TS_ANALYSE_RESULTS_TO_REDIS = False
SAVE_TS_CLASSIFY_RESULTS_TO_REDIS = False
SAVE_TS_CLASSIFY_SUBLOC_RESULTS_TO_REDIS = False
SAVE_TS_CLASSIFY_HOOFDLOC_RENOVATION_MERGED_RESULTS_TO_REDIS = False
SAVE_TS_CLASSIFY_HOOFDLOC_RENOVATION_RAW_AND_MERGED_RESULTS_TO_FILE = True
SAVE_FAILED_TS_ANALYSE_TO_REDIS = False
SAVE_FAILED_TS_CLASSIFY_TO_REDIS = False
SAVE_FAILED_TS_SUBLOC_CLASSIFY_TO_REDIS = False
START_WITH_EMPTY_REDIS_DB = False
UPDATE_RESULT_CSVS_NORMAL_QUARTER_GAPS = False
NORMAL_GAP_MAX_ALLOWED = pd.Timedelta(hours=2)

# BASE_DIR avoid 'Path.cwd()', as wis_timeseries_gapfinder.main() should be callable from everywhere
BASE_DIR = Path(__file__).parent.parent.parent
DATA_INPUT_DIR = BASE_DIR / "data" / "input"
DATA_OUTPUT_DIR = BASE_DIR / "data" / "output"
LOG_DIR = DATA_OUTPUT_DIR / "log_rotating"
LOG_FILE_PATH = LOG_DIR / "main.log"
WIS_CONFIG_DIR = DATA_INPUT_DIR / "fews_config_prd_20220404"  # "fews_config_prd_20220126"
NORMAL_GAPS_RESULTS_PATH = DATA_OUTPUT_DIR / "results_normal_gaps.csv"
QUARTER_GAPS_RESULTS_PATH = DATA_OUTPUT_DIR / "results_quarter_gaps.csv"
PEILGEBIEDEN_SHP_PATH = DATA_INPUT_DIR / "peilgebieden.shp"
AFVOERGEBIEDEN_SHP_PATH = DATA_INPUT_DIR / "afvoergebieden.shp"
KNOWN_RENOVATION_CSV_PATH = DATA_INPUT_DIR / "kw_data_renovation.csv"


GITHUB_ORGANISATION_NAME = "hdsr-mid"
# github repo 'https://github.com/hdsr-mid/startenddate'
GITHUB_STARTENDDATE_REPO_NAME = "startenddate"
GITHUB_STARTENDDATE_BRANCH_NAME = "main"
GITHUB_STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES = timedelta(weeks=52 / 4)
# caw_oppervlaktewater_short = roger's get_histtags -> series is eg. "#001_ES1"
# caw_oppervlaktewater_long = roger's get_series    -> series is eg. "#001_ES1 ['WIJKERSLOOT' || 'Stuw: eindstand op']"
GITHUB_STARTENDDATE_CAW_OPPERVLAKTEWATER_SHORT = Path("data/output/results/caw_oppervlaktewater_short.csv")
# github repo 'https://github.com/hdsr-mid/histtag_ignore'
GITHUB_HISTTAG_IGNORE_REPO_NAME = "histtag_ignore"
GITHUB_HISTTAG_IGNORE_BRANCH_NAME = "main"
GITHUB_HISTTAG_IGNORE = Path("histtag_ignore.csv")
GITHUB_HISTTAG_IGNORE_ALLOWED_PERIOD_NO_UPDATES = timedelta(weeks=52 / 2)


def check_constants_paths():
    assert BASE_DIR.name == "wis_timeseries_gapfinder"
    assert DATA_INPUT_DIR.is_dir()
    assert DATA_OUTPUT_DIR.is_dir()
    assert LOG_DIR.is_dir()
    assert WIS_CONFIG_DIR.is_dir()
