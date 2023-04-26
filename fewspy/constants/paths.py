from pathlib import Path


G_DRIVE = Path("G:/")

BASE_DIR = Path(__file__).parent.parent.parent
TEST_INPUT_DIR = BASE_DIR / "fewspy" / "tests" / "data" / "input"
DEFAULT_OUTPUT_FOLDER = G_DRIVE / "hdsr_fewspy_output"

assert BASE_DIR.is_dir()
assert TEST_INPUT_DIR.is_dir()
assert BASE_DIR.name == "hdsr_fewspy", f"BASE_DIR must be hdsr_fewspy, but is {BASE_DIR.name}"

SECRETS_ENV_PATH = G_DRIVE / "secrets.env"
GITHUB_PERSONAL_ACCESS_TOKEN = "GITHUB_PERSONAL_ACCESS_TOKEN"
HDSR_FEWSPY_EMAIL = "HDSR_FEWSPY_EMAIL"
HDSR_FEWSPY_TOKEN = "HDSR_FEWSPY_TOKEN"
