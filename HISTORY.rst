1.16 (Unreleased)
------------------------
-  

1.15 (2024-04-30)
------------------------
- fix check auth permissions
- enable communication with FEWS-EFCIS webservice
- add get_samples
- ensure flattened pi-events (timeseries events responses are suddenly nested dict)

1.14 (2023-12-20)
------------------------
- handle different timeseries event parameters (e.g. 'comment') in case of not 'only_value_and_flag'
- release for python 3.7 till 3.12

1.13 (2023-12-14)
------------------------
- delete dependency validators
- improve instantiating Retry session
- fix dataclass TimeSeries field events default value
- enable other fields in timeseries response than {timestamp, value, flag} by adding 'only_value_and_flag'
- release for python 3.8 and 3.12

1.12 (2023-08-30)
------------------------
- add logging to examples
- add timeseries flag description (Deltares url) to readme
- add __repr__ to PiSettings so that non-python users (R, etc.) can print those settings
- updated default pi_settings to new datascience FEWS machine (production)
- add hdsr_fewspy.__version__

1.11 (2023-06-01)
------------------------
- handle deprecated requests.packages.urllib3.util.retry.Retry's argument 'method_whitelist'
- add get_time_series pre check 'does ts exists at all without start_time and end_time' to speed up
- speed up get_time_series with first attempt whole time-series period
- distinguish more predefined DefaultPiSettingsChoices: raw, work and validated
- add area pi_settings to enable downloading time-series aggregated to areas

1.10 (2023-05-23)
------------------------
- bug fix: empty get_time_series response previous request
- enable start_time and end_time as strings

1.9 (2023-05-16)
------------------------
- no github_pi_setting_defaults anymore outside Api
- add progress logging to get_time_series_multi()

1.8 (2023-05-10)
------------------------
- remove hdsr_fewspy_token (only use github personal email and token)
- improve logging "code error"

1.7 (2023-05-03)
------------------------
- improve logging _ensure_service_is_running
- add github_pi_setting_defaults to hdsr_fewspy.__init__
- update readme usage examples

1.6 (2023-05-02)
------------------------
- add lazy evaluation of github_pi_setting_defaults

1.5 (2023-05-02)
------------------------
- use DateFrequencyBuilder frequency of previous request avoid all window update iterations
- improve logging (less logging due to info to debug)

1.4 (2023-05-02)
------------------------
- skip responses != 200 (so no custom created xml/json responses)

1.3 (2023-05-01)
------------------------
- keep responses in case of recursive _download_timeseries()

1.2 (2023-04-26)
------------------------
- add OutputChoices and TimeZoneChoices to hdsr_fewspy.__init__
- fix BASE_DIR
- add usage examples to readme

1.1 (2023-04-26)
------------------------
- read on-the-fly default pi_settings from hdsr_fewspy_auth github repo

1.0 (2023-04-26)
------------------------
- add initial code
- test release
