### Context
* Created: April 2023
* Author: Renier Kramer, renier.kramer@hdsr.nl
* Python version: >3.7

[hkvfewspy]: https://github.com/HKV-products-services/hkvfewspy
[fewspy]: https://github.com/d2hydro/fewspy
[MIT]: https://github.com/hdsr-mid/hdsr_fewspy/blob/main/LICENSE.txt
[Deltares FEWS PI]: https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service
[issues page]: https://github.com/hdsr-mid/hdsr_fewspy/issues
[github personal token]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
[releases]: https://pypi.org/project/hdsr-fewspy/#history

### Description
A python project to request data (locations, timeseries, etc.) from a HDSR FEWS PiWebService: FEWS-WIS or FEWS-EFCIS. 
Note that this project only works on HDSR's internal network, so within the VDI. The project combines the best from 
two existing fewspy projects: [fewspy] and [hkvfewspy]. On top of that it adds client-side authentication, 
authorisation, and throttling. The latter is to minimize request load on HDSR's internal FEWS instances. 

Hdsr_fewspy API support 9 different API calls that can return 6 different output formats:   
1. xml_file_in_download_dir: The xml response is written to a .xml file in your download_dir
2. json_file_in_download_dir: The json response is written to a .json file in your download_dir
3. csv_file_in_download_dir: The json response is converted to csv and written to a .csv file in your download_dir
4. xml_response_in_memory: the xml response is returned memory meaning you get a list with one or more responses 
5. json_response_in_memory: the json response is returned memory meaning you get a list with one or more responses        
6. pandas_dataframe_in_memory: the json response is converted to a pandas dataframe meaning you get one dataframe 

API call                      | Supported outputs  | Notes 
------------------------------|--------------------|--------
get_parameters                | 4, 5, 6            | Returns 1 object (xml/json response or dataframe) 
get_filters                   | 4, 5               | Returns 1 object (xml/json response)  
get_locations                 | 4, 5               | Returns 1 object (xml/json response)              
get_qualifiers                | 4, 6               | Returns 1 object (xml response or dataframe)
get_timezone_id               | 4, 5               | Returns 1 object (xml/json response)
get_samples                   | TODO               | Not implemented yet
get_time_series_single        | 4, 5, 6            | Returns 1 dataframe or a list >=1 xml/json responses     
get_time_series_multi         | 1, 2, 3            | Returns a list with downloaded files (1 .csv or >=1 .xml/.json per unique location_parameter_qualifier)
get_time_series_statistics    | 4, 5               | Returns 1 object (xml/json response)

### Usage

###### Preparation
1. Only once needed: ensure you have a github account with a GITHUB_PERSONAL_ACCESS_TOKEN. Read topic 
   'GITHUB_PERSONAL_ACCESS_TOKEN' below.
2. You can create a hdsr_fewspy API in two ways (the first dominates the second): 
   a. or with API argument 'github_personal_access_token'
   b. or with API argument 'secrets_env_path' (defaults to 'G:/secrets.env'). The .env file must have a row:
```
GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_token>
```
3. Only once per project: install hdsr_fewspy dependency:
```
pip install hdsr-fewspy 
# or 
conda install hdsr-fewspy --channel hdsr-mid
```
4. Example simple:
```
import hdsr_fewspy

api = hdsr_fewspy.Api()
```
5. Example sophisticated:
```
import hdsr_fewspy

# Optionally, you can specify several API arguments:
# github_email: str, 
# github_personal_access_token: str
# secrets_env_path: str or pathlib.Path
# pi_settings: hdsr_fewspy.PiSettings 
# output_directory_root: str or pathlib.path

# For example in case of pi_settings, you can use predefined settings ('wis_production', 'efcis_production', etc.):
api = hdsr_fewspy.Api(pi_settings=DefaultPiSettingsChoices.wis_stand_alone)

# Or create your own pi_settings:
custom_settings = hdsr_fewspy.PiSettings(
   settings_name="does not matter blabla",         
   document_version=1.25,
   ssl_verify=True,
   domain="localhost",
   port=8080,
   service="FewsWebServices",
   filter_id="INTERNAL-API",
   module_instance_ids="WerkFilter",
   time_zone=hdsr_fewspy.TimeZoneChoices.eu_amsterdam,  # = 1.0 (only affects get_time_series dataframe and csv)
)
api = hdsr_fewspy.Api(pi_settings=custom_settings)

# In case you want to download responses to file, then you need to specify an output_directory_root 
# The files will be downloaded in a subdir: output_directory_root/hdsr_fewspy_<datetime>/<files_will_be_downloaded_here>
api = hdsr_fewspy.Api(output_directory_root=<path_to_a_dir>)
```

###### Examples 9 different API calls (using api option 3 from above)
1. get_parameters
```
df = api.get_parameters(output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory)

# id       name                                parameter_type unit display_unit uses_datum parameter_group  
# ---------------------------------------------------------------------------------------------------------                                                                                                                                 
# BG.b.0   Oppervlaktebegroeiing [%] - noneq   instantaneous  %    %            False      Begroeiingsgraad   
# BG.fd.0  Flab en draadwieren [%] - noneq     instantaneous  %    %            False      Begroeiingsgraad   
# BG.ka.0  Algen-/kroosbedekking [%] - noneq   instantaneous  %    %            False      Begroeiingsgraad  
# ...etc...
```
2. get_filters
```
response = api.get_filters(output_choice=hdsr_fewspy.OutputChoices.json_response_in_memory)
response.json() 

# {
# "version": "1.25",
# "filters": [
#     {
#         "id": "INTERNAL-API",
#         "name": "INTERNAL-API",
#         "child": [{"id": "INTERNAL-API.RUWMET", "name": "Ruwe metingen (punt)"
# ...etc...
```
3. get_locations
```
gdf = get_locations(output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory, show_attributes=True)

# location_id description          short_name          lat               lon                x        y        z   parent_location_id geometry                      attributes
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                                                  
# beg_062     BEGROEIINGSMEETPUNT  beg_062-LR_13_xruim 52.58907339700342 5.1718081593021505 140251.0 460118.0 0.0 NaN                POINT (140251.000 460118.000) [{'name': 'LOC_NAME', 'type': 'text', 'id': 'LOC_NAME', 'value': 'beg_062 ...etc...]
# beg_084     BEGROEIINGSMEETPUNT  beg_084-LR_17_xruim 52.06261306007392 5.12600382893812   137088.0 452734.0 0.0 NaN                POINT (137088.000 452734.000) [{'name': 'LOC_NAME', 'type': 'text', 'id': 'LOC_NAME', 'value': 'beg_084 ...etc...]
# beg_102     BEGROEIINGSMEETPUNT  beg_102-KR_9_xruim  52.07249358678008 5.215531005948442  143230.0 453815.0 0.0 NaN                POINT (143230.000 453815.000) [{'name': 'LOC_NAME', 'type': 'text', 'id': 'LOC_NAME', 'value': 'beg_102 ...etc...]
# ...etc...
```
4. get_qualifiers
```
df = fixture_api_sa_no_download_dir.get_qualifiers(output_choice=hdsr_fewspy.OutputChoices.pandas_dataframe_in_memory)
    
# id      name               group_id
# -----------------------------------
# ergkrap erg krap (max 10%) None
# krap    krap (max 30%)     None
# normaal normaal (max 50%)  None
# ruim    ruim (max 70%)     None
# ...etc...
```

5. get_timezone_id
```
response = api.get_timezone_id(output_choice=hdsr_fewspy.OutputChoices.json_response_in_memory)

# verify response
assert response.text == "GMT"
assert TimeZoneChoices.get_tz_float(value=response.text) == TimeZoneChoices.gmt == 0.0
```
6. get_samples
```
# Not yet implemented
```
7. get_time_series_single
```
# Single means: use max 1 location_id and/or parameter_id and/or qualifier_id. One large call can result in multiple 
# small calls and therefore multiple responses. If your output_choice is json/xml in memory, then you get a list with 
# >=1 responses. Arguments 'flag_threshold' and 'drop_missing_values' have no effect.  

from datetime import datetime
responses = api.get_time_series_single(
    location_id = "OW433001",
    parameter_id = "H.G.0",
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.xml_response_in_memory,
)

print(responses[0].text)
# <?xml version="1.0" encoding="UTF-8"?>
# <TimeSeries xmlns="http://www.wldelft.nl/fews/PI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews/PI http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd" version="1.25" xmlns:fs="http://www.wldelft.nl/fews/fs">
#     <timeZone>0.0</timeZone>
#     <series>
#         <header>
#             <type>instantaneous</type>
#             <moduleInstanceId>WerkFilter</moduleInstanceId>
#             <locationId>OW433001</locationId>
#             <parameterId>H.G.0</parameterId>
#             <timeStep unit="nonequidistant"/>
#             <startDate date="2012-01-01" time="00:00:00"/>
#             <endDate date="2012-01-02" time="00:00:00"/>
#             <missVal>-999.0</missVal>
#             <stationName>HAANWIJKERSLUIS_4330-w_Leidsche Rijn</stationName>
#             <lat>52.08992726570302 asdf renier</lat>
#             <lon>4.9547458967486095</lon>
#             <x>125362.0</x>
#             <y>455829.0</y>
#             <z>-0.18</z>
#             <units>mNAP</units>
#         </header>
#         <event date="2012-01-01" time="00:15:00" value="-0.35" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
#         <event date="2012-01-01" time="00:45:00" value="-0.36" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
#         <event date="2012-01-01" time="02:30:00" value="-0.37" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
#         <event date="2012-01-01" time="02:31:17" value="-0.38" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
#         <event date="2012-01-01" time="03:15:00" value="-0.39" flag="0" fs:PRIMAIR="OK" fs:VISUEEL="OK"/>
#         ...etc..

# If your output_choice is dataframe, then all responses are collected in one dataframe. Arguments 'flag_threshold' 
# and 'drop_missing_values' do have effect.

df = api.get_time_series_single(
    location_id = "OW433001",
    parameter_id = "H.G.0",
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    drop_missing_values = True,
    flag_threshold = 6,  # all flags 6 and higher are removed from dataframe
    output_choice = OutputChoices.pandas_dataframe_in_memory,
)
```
8. get_time_series_multi 
```
# Multi means: use >=1 location_id and/or parameter_id and/or qualifier_id. The api call below results in 4 unique 
# location_parameter_qualifier comibinations: OW433001_hg0, OW433001_hgd, OW433002_hg0, OW433002_hgd. Per unique 
# combination we do >=1 requests which therefore result in >=1 responses. If output_choice is xml/json to file, then 
# each response results in a file. Arguments 'flag_threshold' and 'drop_missing_values' have no effect.  

from datetime import datetime
list_with_donwloaded_csv_filepaths = api.get_time_series_multi(
    location_ids = ["OW433001", "OW433002"]
    parameter_ids = ["H.G.0", "H.G.d"],
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.xml_file_in_download_dir,
)

print(list_with_donwloaded_csv_filepaths)
# <output_directory_root>/hdsr_fewspy_<datetime>/gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z_0.json
# <output_directory_root>/hdsr_fewspy_<datetime>/gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z_0.json
# <output_directory_root>/hdsr_fewspy_<datetime>/gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z_1.json


# If output_choice is csv to file, then all responses per unique combi are grouped in one csv file. Arguments 
# 'flag_threshold' and 'drop_missing_values' do have effect.
  
list_with_donwloaded_csv_filepaths = api.get_time_series_multi(
    location_ids = ["OW433001", "OW433002"]
    parameter_ids = ["H.G.0", "H.G.d"],
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.csv_file_in_download_dir,
)

print(list_with_donwloaded_csv_filepaths) 
# <output_directory_root>/hdsr_fewspy_<datetime>/gettimeseriesmulti_ow433001_hg0_20120101t000000z_20120102t000000z.csv
# <output_directory_root>/hdsr_fewspy_<datetime>/gettimeseriesmulti_ow433002_hg0_20120101t000000z_20120102t000000z.csv
```
9. get_time_series_statistics
```
from datetime import datetime
response = api.get_time_series_statistics(
    location_id = "OW433001",
    parameter_id = "H.G.0",
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.json_response_in_memory
)

print(response.text)
# {
#    "timeSeries": [
#        {
#            "header": {
#                "endDate": {"date": "2012-01-02", "time": "00:00:00"},
#                "firstValueTime": {"date": "2012-01-01", "time": "00:15:00"},
#                "lastValueTime": {"date": "2012-01-02", "time": "00:00:00"},
#                "lat": "52.08992726570302",
#                "locationId": "OW433001",
#                "lon": "4.9547458967486095",
#                "maxValue": "-0.28",
#                "minValue": "-0.44",
#                "missVal": "-999.0",
#                "moduleInstanceId": "WerkFilter",
#                "parameterId": "H.G.0",
#                "startDate": {"date": "2012-01-01", "time": "00:00:00"},
#                "stationName": "HAANWIJKERSLUIS_4330-w_Leidsche " "Rijn",
#                "timeStep": {"unit": "nonequidistant"},
#                "type": "instantaneous",
#                "units": "mNAP",
#                "valueCount": "102",
#                "x": "125362.0",
#                "y": "455829.0",
#                "z": "-0.18",
#            }
#        }
#    ]
# }       
```

######  GITHUB_PERSONAL_ACCESS_TOKEN
A github personal token (a long hash) has to be created once and updated when it expires. You can have maximum 1 token.
This token is related to your github user account, so you don't need a token per repo/organisation/etc. 
You can [create a token yourself][[github personal token]]. In short:
1. Login github.com with your account (user + password)
2. Ensure you have at least read-permission for the hdsr-mid repo(s) you want to interact with. To verify, browse to 
   the specific repo. If you can open it, then you have at least read-permission. If not, please contact 
   renier.kramer@hdsr.nl to get access.
3. Create a token:
   1. On github.com, go to your profile settings (click your icon right upper corner and 'settings' in the dropdown).
   2. Click 'developer settings' (left lower corner).
   3. Click 'Personal access tokens' and then 'Tokens (classic)'.
   4. Click 'Generate new token' and then 'Generate new token (classic)'.
4. We recommend setting an expiry date of max 1 year (for safety reasons).
5. Create a file (Do not share this file with others!) on your personal HDSR drive 'G:/secrets.env' and add a line: 
   GITHUB_PERSONAL_ACCESS_TOKEN=<your_token>
   

### License 
[MIT]

### Releases
[Release history][releases]

### Contributions
All contributions, bug reports, documentation improvements, enhancements and ideas are welcome on the [issues page].

### Test Coverage (May 16th 2023)
```
---------- coverage: platform win32, python 3.7.12-final-0 -----------
Name                                                              Stmts   Miss  Cover
-------------------------------------------------------------------------------------
hdsr_fewspy\__init__.py                                              10      0   100%
hdsr_fewspy\api.py                                                  110     16    85%
hdsr_fewspy\api_calls\__init__.py                                    18      0   100%
hdsr_fewspy\api_calls\base.py                                       100     12    88%
hdsr_fewspy\api_calls\get_filters.py                                 25      0   100%
hdsr_fewspy\api_calls\get_locations.py                               44      2    95%
hdsr_fewspy\api_calls\get_parameters.py                              40      1    98%
hdsr_fewspy\api_calls\get_qualifiers.py                              50     16    68%
hdsr_fewspy\api_calls\get_samples.py                                 24      8    67%
hdsr_fewspy\api_calls\get_timezone_id.py                             26      1    96%
hdsr_fewspy\api_calls\time_series\base.py                           109      9    92%
hdsr_fewspy\api_calls\time_series\get_time_series_multi.py           73      6    92%
hdsr_fewspy\api_calls\time_series\get_time_series_single.py          35      2    94%
hdsr_fewspy\api_calls\time_series\get_time_series_statistics.py      23      2    91%
hdsr_fewspy\constants\choices.py                                     89      3    97%
hdsr_fewspy\constants\custom_types.py                                 2      0   100%
hdsr_fewspy\constants\github.py                                       8      0   100%
hdsr_fewspy\constants\paths.py                                       10      0   100%
hdsr_fewspy\constants\pi_settings.py                                 78      7    91%
hdsr_fewspy\constants\request_settings.py                            12      0   100%
hdsr_fewspy\converters\download.py                                   82      4    95%
hdsr_fewspy\converters\json_to_df_timeseries.py                     112      8    93%
hdsr_fewspy\converters\manager.py                                    27      0   100%
hdsr_fewspy\converters\utils.py                                      45     17    62%
hdsr_fewspy\converters\xml_to_python_obj.py                         105     27    74%
hdsr_fewspy\date_frequency.py                                        46      5    89%
hdsr_fewspy\exceptions.py                                            14      0   100%
hdsr_fewspy\permissions.py                                           47      1    98%
hdsr_fewspy\retry_session.py                                         68     12    82%
hdsr_fewspy\secrets.py                                               71     19    73%
setup.py                                                             10     10     0%
-------------------------------------------------------------------------------------
TOTAL                                                              1513    188    88%
```

### Conda general tips
#### Build conda environment (on Windows) from any directory using environment.yml:
Note1: prefix is not set in the environment.yml as then conda does not handle it very well
Note2: env_directory can be anywhere, it does not have to be in your code project
```
> conda env create --prefix <env_directory><env_name> --file <path_to_project>/environment.yml
# example: conda env create --prefix C:/Users/xxx/.conda/envs/project_xx --file C:/Users/code_projects/xx/environment.yml
> conda info --envs  # verify that <env_name> (project_xx) is in this list 
```
#### Start the application from any directory:
```
> conda activate <env_name>
# At any location:
> (<env_name>) python <path_to_project>/main.py
```
#### Test the application:
```
> conda activate <env_name>
> cd <path_to_project>
> pytest  # make sure pytest is installed (conda install pytest)
```
#### List all conda environments on your machine:
```
At any location:
> conda info --envs
```
#### Delete a conda environment:
```
Get directory where environment is located 
> conda info --envs
Remove the enviroment
> conda env remove --name <env_name>
Finally, remove the left-over directory by hand
```
#### Write dependencies to environment.yml:
The goal is to keep the .yml as short as possible (not include sub-dependencies), yet make the environment 
reproducible. Why? If you do 'conda install matplotlib' you also install sub-dependencies like pyqt, qt 
icu, and sip. You should not include these sub-dependencies in your .yml as:
- including sub-dependencies result in an unnecessary strict environment (difficult to solve when conflicting)
- sub-dependencies will be installed when dependencies are being installed
```
> conda activate <conda_env_name>

Recommended:
> conda env export --from-history --no-builds | findstr -v "prefix" > --file <path_to_project>/environment_new.yml   

Alternative:
> conda env export --no-builds | findstr -v "prefix" > --file <path_to_project>/environment_new.yml 

--from-history: 
    Only include packages that you have explicitly asked for, as opposed to including every package in the 
    environment. This flag works regardless how you created the environment (through CMD or Anaconda Navigator).
--no-builds:
    By default, the YAML includes platform-specific build constraints. If you transfer across platforms (e.g. 
    win32 to 64) omit the build info with '--no-builds'.
```
#### Pip and Conda:
If a package is not available on all conda channels, but available as pip package, one can install pip as a dependency.
Note that mixing packages from conda and pip is always a potential problem: conda calls pip, but pip does not know 
how to satisfy missing dependencies with packages from Anaconda repositories. 
```
> conda activate <env_name>
> conda install pip
> pip install <pip_package>
```
The environment.yml might look like:
```
channels:
  - defaults
dependencies:
  - <a conda package>=<version>
  - pip
  - pip:
    - <a pip package>==<version>
```
You can also write a requirements.txt file:
```
> pip list --format=freeze > <path_to_project>/requirements.txt
```
