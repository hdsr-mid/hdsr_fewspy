1.9 (Unreleased)
----------------

1.8 (2023-05-10)
----------------
- remove hdsr_fewspy_token (only use github personal email and token)
- improve logging "code error"

1.7 (2023-05-03)
----------------
- improve logging _ensure_service_is_running
- add github_pi_setting_defaults to hdsr_fewspy.__init__
- update readme usage examples

1.6 (2023-05-02)
----------------
- add lazy evaluation of github_pi_setting_defaults

1.5 (2023-05-02)
----------------
- use DateFrequencyBuilder frequency of previous request avoid all window update iterations
- improve logging (less logging due to info to debug)

1.4 (2023-05-02)
----------------
- skip responses != 200 (so no custom created xml/json responses)

1.3 (2023-05-01)
----------------
- keep responses in case of recursive _download_timeseries()

1.2 (2023-04-26)
----------------
- add OutputChoices and TimeZoneChoices to hdsr_fewspy.__init__
- fix BASE_DIR
- add usage examples to readme

1.1 (2023-04-26)
----------------
- read on-the-fly default pi_settings from hdsr_fewspy_auth github repo

1.0 (2023-04-26)
----------------
- add initial code
- test release
