### Context
* Created: November 2021
* Author: Renier Kramer, renier.kramer@hdsr.nl
* Python version: >3.5

### Description
A python project that uses [hkvfewspy][hkvfewspy_link] - which is a Python wrapper for Delft 
Fews-PI sevices developed by HKV - to retrieve data from HDSR FEWS-WIS.

### Usage
1. build conda environment from file if you don't have environment already
```
> conda env create --name hdsr_hkvfewspy --file <path_to_project>/environment.yml
```
2. run project:
```
> conda activate hdsr_hkvfewspy
> python <path_to_project>/main.py
```
3. example how to use see [these notebooks][notebooks] 

### License 
[MIT][mit]

[hkvfewspy_link]: https://github.com/HKV-products-services/hkvfewspy
[notebooks]: https://github.com/HKV-products-services/hkvfewspy/tree/master/notebooks 
[mit]: https://github.com/hdsr-mid/mwm_ps_update/blob/main/LICENSE.txt

### Releases
None

### Contributions
All contributions, bug reports, bug fixes, documentation improvements, enhancements 
and ideas are welcome on https://github.com/hdsr-mid/hdsr_hkvfewspy/issues

### Test Coverage 
Project holds no tests

### Conda general tips
#### Build conda environment (on Windows) from any directory using environment.yml:
```
> conda env create --name <conda_env_name> --file <path_to_project>/environment.yml python=<python_version>
> conda info --envs  # verify that <conda_env_name> is in this list 
```
#### Start the application from any directory:
```
> conda activate <conda_env_name>
At any location:
> (<conda_env_name>) python <path_to_project>/main.py
```
#### Test the application:
```
> conda activate <conda_env_name>
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
> conda env remove --name <conda_env_name>
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
> conda activate <conda_env_name>
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
