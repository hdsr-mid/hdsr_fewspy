### Context
* Created: February 2023
* Author: Renier Kramer, renier.kramer@hdsr.nl
* Python version: >3.7

[hkvfewspy]: https://github.com/HKV-products-services/hkvfewspy
[fewspy]: https://github.com/d2hydro/fewspy
[MIT]: https://github.com/hdsr-mid/hdsr_fewspy/blob/main/LICENSE.txt
[Deltares FEWS PI]: https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service
[issues page]: https://github.com/hdsr-mid/hdsr_fewspy/issues

### Description
A python project to request data (locations, timeseries, etc.) from a HDSR FEWS PiWebService: FEWS-WIS or FEWS-EFCIS. 
Note that this project only works on HDSR's internal network, so within the VDI. 
The project combines the best from two existing fewspy projects: [fewspy] and [hkvfewspy]. On top of that it adds 
"authentication" and "throttling" to minimize request load on HDSR's internal FEWS instances.

### Usage 
TODO

### License 
[MIT]

### Releases
TODO

### Contributions
All contributions, bug reports, documentation improvements, enhancements and ideas are welcome on the [issues page].

### Test Coverage (17 april 2023)
```
---------- coverage: platform win32, python 3.7.12-final-0 -----------
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
fewspy\api.py                             57     18    68%
fewspy\constants\choices.py               33      1    97%
fewspy\constants\paths.py                  3      0   100%
fewspy\constants\pi_settings.py           45      4    91%
fewspy\constants\request_settings.py      11      0   100%
fewspy\exceptions.py                      28      2    93%
fewspy\retry_session.py                   66     12    82%
fewspy\time_series.py                     99      9    91%
fewspy\utils\conversions.py               50     27    46%
fewspy\utils\timer.py                     17      5    71%
fewspy\utils\transformations.py           21      2    90%
fewspy\wrappers\__init__.py               14      0   100%
fewspy\wrappers\get_filters.py            18     11    39%
fewspy\wrappers\get_locations.py          28     17    39%
fewspy\wrappers\get_parameters.py         23     14    39%
fewspy\wrappers\get_qualifiers.py         33     19    42%
fewspy\wrappers\get_samples.py            13      5    62%
fewspy\wrappers\get_time_series.py        24      1    96%
fewspy\wrappers\get_timezone_id.py        15      1    93%
main.py                                   27     27     0%
----------------------------------------------------------
TOTAL                                    625    175    72%
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
At any location:
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
