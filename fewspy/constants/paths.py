from pathlib import Path


G_DRIVE = Path("G:/")

BASE_DIR = Path(__file__).parent.parent.parent
assert BASE_DIR.name == "hdsr_fewspy", f"BASE_DIR must be hdsr_fewspy, but is {BASE_DIR.name}"

main_ns = {}
version_path = BASE_DIR / "fewspy" / "version.py"
assert version_path.is_file()
with open(version_path) as version_file:
    exec(version_file.read(), main_ns)

HDSR_FEWSPY_VERSION = main_ns["__version__"]

DEFAULT_OUTPUT_FOLDER = G_DRIVE / "hdsr_fewspy_output"
