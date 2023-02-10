# performance-path-compliance-check-tool

## Prerequisite

Require Ruby v2.7
Require Python ~3.7+

1. Install OpenStudio SDK v3.2 and above. Download in this [link](https://openstudio.net/downloads).
2. Install latest OpenStudio Standard - a detail instruction is provided in the [OpenStudio Standard user documentation](https://pnnl.github.io/BEM-for-PRM)
3. Install EnergyPlus v9.6 and above. Download in this [link](https://energyplus.net/downloads).
4. Install createRulesetModelDescription package. Download in this [link](https://github.com/JasonGlazer/createRulesetModelDescription).
5. Install ruleset-checking-tool package. Download in this [link](https://github.com/pnnl/ruleset-checking-tool/tree/develop)

## How to use

#### Step 1: generate prototype model and baseline model
Step 1 require using the `osstd_model_generate.rb` script.

```ruby
# Project data shall be the strings copied from:
# https://pnnl.github.io/BEM-for-PRM/user_guide/prm_api_ref/baseline_generation_api/
code_version = '90.1-2004'
bldg_type = 'SmallOffice'
# make sure climate_zone and epw_file are aligned
climate_zone = 'ASHRAE 169-2013-2A'
epw_file = 'C:\EnergyPlusV9-6-0\WeatherData\USA_FL_Tampa.Intl.AP.722110_TMY3.epw'
default_hvac_bldg_type = 'other nonresidential'
default_wwr_bldg_type = 'Office <= 5,000 sq ft'
default_swh_bldg_type = 'Office'

```
The meta data at the top of the script can be modified accordingly.

#### Step 2: Run simulation and performance checking
This step uses the `demo_client.py` script.

```python
sys.path.append("C:\\Users\\[USER_NAME]\\Documents\\GitHub\\createRulesetModelDescription")

## Step 1: Modify RCT directory
RCT_DIR = "C:\\Users\\[USER_NAME]\\Documents\\GitHub\\ruleset-checking-tool\\"
## Step 2: Modify weather file directory
WEA_PATH = "C:\\EnergyPlusV9-6-0\\WeatherData\\USA_FL_Tampa.Intl.AP.722110_TMY3.epw"
## Step 3: Set your EnergyPlus directory (has to be 22.2 or higher)
EPLUS_DIR = "C:\\EnergyPlusV22-2-0\\"
## Step 4: Set the baseline & proposed model IDF version
OSSTD_EPLUS_VER = "V22-1-0"
```
The `sys.path.append()` shall pointing to the path of your local `createRulesetModelDescription`.
Also, note the `OSSTD_EPLUS_VER` indicates the version of EnergyPlus in the models generated in Step 1.
For example, if using OpenStudio SDK 3.5, then the EnergyPlus version is probably `V22-2-0`.
The [link](https://github-wiki-see.page/m/NREL/OpenStudio/wiki/OpenStudio-SDK-Version-Compatibility-Matrix) contains the version matrix of OpenStudio SDK for reference.

Run the script will generate the output report for review.