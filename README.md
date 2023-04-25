### Context
* Created: February 2023
* Author: Renier Kramer, renier.kramer@hdsr.nl
* Python version: >3.7

[hkvfewspy]: https://github.com/HKV-products-services/hkvfewspy
[fewspy]: https://github.com/d2hydro/fewspy
[MIT]: https://github.com/hdsr-mid/hdsr_fewspy/blob/main/LICENSE.txt
[Deltares FEWS PI]: https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service
[issues page]: https://github.com/hdsr-mid/hdsr_fewspy/issues
[github personal token]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token


### Description
A python project to request data (locations, timeseries, etc.) from a HDSR FEWS PiWebService: FEWS-WIS or FEWS-EFCIS. 
Note that this project only works on HDSR's internal network, so within the VDI. The project combines the best from 
two existing fewspy projects: [fewspy] and [hkvfewspy]. On top of that it adds authentication, authorisation, and 
throttling. The latter is to minimize request load on HDSR's internal FEWS instances. 

Hdsr_fewspy API support 9 different API calls:
1. get_parameters:
2. get_filters:
3. get_locations:
4. get_qualifiers: 
5. get_timezone_id: 
6. get_samples: 
7. get_time_series_single: 
8. get_time_series_multi:
9: get_time_series_statistics:

An API call can return 6 different output formats:   
1. xml_file_in_download_dir: The xml response is written to a .xml file in your download_dir
2. json_file_in_download_dir: The json response is written to a .json file in your download_dir
3. csv_file_in_download_dir: The json response is converted to csv and written to a .csv file in your download_dir
4. xml_response_in_memory: the xml response is returned memory meaning you get a list with one or more responses 
5. json_response_in_memory: the json response is returned memory meaning you get a list with one or more responses        
6. pandas_dataframe_in_memory: the json response is converted to a pandas dataframe meaning you get one dataframe 

Each API call supports a subset of output formats:

API call| Supported outputs | Notes 
--------|-------------------|--------
1       | 4, 5              | Not implemented yet
2       | 4, 5              | Not implemented yet  
3       | 4, 5              | Not implemented yet              
4       | 4, 5              | Not implemented yet
5       | 4, 5              | Not implemented yet
6       | 1, 2              | Not implemented yet
7       | 4, 5, 6           | One large call can results in multiple small calls. Output 4 and 5 return a list with >=1 responses. Output 6 aggregates all responses and returns one dataframe.    
8       | 1, 2, 3           | One unique location_parameter_qualifier combination results in >=1 API calls = >=1 responses. For output 1 and 2 each response results in 1 file. Output 3 creates 1 csv per unique combination.
9       | 4, 5              | Not implemented yet 

### Usage

###### Preparation
1. Only once needed: ensure you have a file G:/secrets.env. This file must contain at least these 3 lines:
```
GITHUB_PERSONAL_ACCESS_TOKEN=<see topic 'GITHUB_PERSONAL_ACCESS_TOKEN' below>
HDSR_FEWSPY_EMAIL=<your_hdsr_email>
HDSR_FEWSPY_TOKEN=<contact renier.kramer.hdsr.nl to get HDSR_FEWSPY_TOKEN>
```
2. Only once per project: install hdsr_fewspy dependency
```
pip install hdsr_fewspy 
or 
conda install hdsr_fewspy -c hdsr-mid
```
3. Run imports and instantiate hdsr_fewspy API 
```
from hdsr_fewspy import API, OutputChoices
from datetime import datetime

# instantiate API using default settings
api = Api()

# instantiate API using custom settings


```
###### Examples different API calls
1. Example get_time_series_single
```
api = Api()

responses = api.get_time_series_single(
    location_id = "OW433001",
    parameter_id = "H.G.0",
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.xml_response_in_memory,
)
```
2. Example get_time_series_multi
```
# we need a download dir for this!
output_directory_root='xxx'
api = Api(output_directory_root=output_directory_root)
list_of_donwloaded_file_paths = api.get_time_series_multi(
    location_ids = ["OW433001", "OW433002"]
    parameter_ids = ["H.G.0", "H.G.d"],
    start_time = datetime(year=2012, month=1, day=1),
    end_time = datetime(year=2012, month=1, day=2),
    output_choice = OutputChoices.csv_file_in_download_dir,
)

# all these donwloaded_file_path are in a sub directory the root dir you used:
print(api.output_dir)
# results in "xxx/hdsr_fewspy_20230419_143834"
```


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
TODO

### Contributions
All contributions, bug reports, documentation improvements, enhancements and ideas are welcome on the [issues page].

### Test Coverage (25 april 2023)
```
---------- coverage: platform win32, python 3.7.12-final-0 -----------
Name                                                         Stmts   Miss  Cover
--------------------------------------------------------------------------------
fewspy\api.py                                                  101     16    84%
fewspy\api_calls\__init__.py                                    18      0   100%
fewspy\api_calls\base.py                                        77      9    88%
fewspy\api_calls\get_filters.py                                 22      0   100%
fewspy\api_calls\get_locations.py                               21      6    71%
fewspy\api_calls\get_parameters.py                              37      1    97%
fewspy\api_calls\get_qualifiers.py                              33     11    67%
fewspy\api_calls\get_samples.py                                 23      7    70%
fewspy\api_calls\get_timezone_id.py                             23      1    96%
fewspy\api_calls\time_series\base.py                            91      9    90%
fewspy\api_calls\time_series\get_time_series_multi.py           67      5    93%
fewspy\api_calls\time_series\get_time_series_single.py          27      1    96%
fewspy\api_calls\time_series\get_time_series_statistics.py      14      0   100%
fewspy\constants\choices.py                                     73      1    99%
fewspy\constants\custom_types.py                                 2      0   100%
fewspy\constants\github.py                                       7      0   100%
fewspy\constants\paths.py                                       19      0   100%
fewspy\constants\pi_settings.py                                 50      4    92%
fewspy\constants\request_settings.py                            11      0   100%
fewspy\converters\download.py                                   93      4    96%
fewspy\converters\json_to_df_timeseries.py                     110      8    93%
fewspy\converters\manager.py                                    27      0   100%
fewspy\converters\xml_to_python_obj.py                         105     26    75%
fewspy\exceptions.py                                            12      0   100%
fewspy\permissions.py                                           68      5    93%
fewspy\retry_session.py                                         68     12    82%
fewspy\secrets.py                                               64     20    69%
fewspy\utils\bug_report.py                                      60     38    37%
fewspy\utils\conversions.py                                     50     27    46%
fewspy\utils\date_frequency.py                                  46      5    89%
fewspy\version.py                                                2      2     0%
main.py                                                         27     27     0%
setup.py                                                        16     16     0%
--------------------------------------------------------------------------------
TOTAL                                                         1464    261    82%
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
