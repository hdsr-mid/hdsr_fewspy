from pathlib import Path


# BASE_DIR avoid 'Path.cwd()', as wis_timeseries_gapfinder.main() should be callable from everywhere
BASE_DIR = Path(__file__).parent.parent
assert BASE_DIR.name == "hdsr_fewspy", f"BASE_DIR must be hdsr_fewspy, but is {BASE_DIR.name}"
