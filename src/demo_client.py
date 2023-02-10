import os
import sys
sys.path.append("C:\\Users\\xuwe123\\Documents\\GitHub\\createRulesetModelDescription")
from eplus_rmd.translator import Translator
from pathlib import Path
from user_data_reader import space_to_ltg_type_map
from preprocess_simulation import version_upgrader, modify_idfs_for_rmd
import json
import subprocess
import shutil
from run_eplus import run

## Step 1: Modify RCT directory
RCT_DIR = "C:\\Users\\xuwe123\\Documents\\GitHub\\ruleset-checking-tool\\"
## Step 2: Modify weather file directory
WEA_PATH = "C:\\EnergyPlusV9-6-0\\WeatherData\\USA_FL_Tampa.Intl.AP.722110_TMY3.epw"
## Step 3: Set your EnergyPlus directory (has to be 22.2 or higher)
EPLUS_DIR = "C:\\EnergyPlusV22-2-0\\"
## Step 4: Set the baseline & proposed model IDF version
OSSTD_EPLUS_VER = "V22-1-0"
FILE_PATH = os.path.dirname(__file__)

def generate_rmd(input_path, model_name):
	translator = Translator(Path(input_path), model_name)
	translator.process()

def replace_lighting_space(rmd_dir):
	rmd_model = {}
	with open(rmd_dir, "r") as rmd:
		rmd_model = json.load(rmd)
		zones = rmd_model["ruleset_model_instances"][0]["buildings"][0]["building_segments"][0]["zones"]
		for zone in zones:
			# remove the trailing ZN
			zone_name = zone["id"].split(" ")[0].lower()
			if space_to_ltg_type_map.get(zone_name):
				print("----------> Set space: %s lighting_space_type to: %s." % (zone["spaces"][0]["id"], space_to_ltg_type_map[zone_name]))
				zone["spaces"][0]["lighting_space_type"] = space_to_ltg_type_map[zone_name]
	with open(rmd_dir, "w") as rmd:
		json.dump(rmd_model, rmd, indent=2)

# Move the generated baseline IDF and proposed IDF to the target folder
print("########################### Prepare models for simulation #############################")
original_proposed_path = os.path.join(FILE_PATH, "../source/proposed_model.idf")
original_baseline_path = os.path.join(FILE_PATH, "../output/final.idf")
space_name_csv = os.path.join(FILE_PATH, "../output/model_space_name.csv")
target_proposed_path = os.path.join(FILE_PATH, "../eplus_sim/proposed/proposed_model.idf")
target_baseline_path = os.path.join(FILE_PATH, "../eplus_sim/baseline/baseline_model.idf")

print("->>>>>>>>>>>>>>>>>>>>> Upgrade Eplus version from 22.1.0 to 22.2.0 >>>>>>>>>>>>>>>>>>")
version_upgrader(OSSTD_EPLUS_VER, original_baseline_path)
version_upgrader(OSSTD_EPLUS_VER, original_proposed_path)

print("->>>>>>>>>>>>>>>>>>>>> Insert user data >>>>>>>>>>>>>>>>>>")
modify_idfs_for_rmd(original_baseline_path, space_name_csv)
modify_idfs_for_rmd(original_proposed_path, space_name_csv)

print("->>>>>>>>>>>>>>>>>>>>> Copy files to target folder >>>>>>>>>>>>>>>>>>")
shutil.copy2(original_proposed_path, target_proposed_path)
shutil.copy2(original_baseline_path, target_baseline_path)

print("######################################### Running simulations")
run(WEA_PATH, target_proposed_path, "proposed_modelout")
run(WEA_PATH, target_baseline_path, "baseline_modelout")

# Convert IDFs to epJSON
subprocess.run(["ConvertInputFormat", target_proposed_path], cwd=EPLUS_DIR, shell=True)
subprocess.run(["ConvertInputFormat", target_baseline_path], cwd=EPLUS_DIR, shell=True)

baseline_dir = os.path.join(FILE_PATH, "../eplus_sim/baseline/")
proposed_dir = os.path.join(FILE_PATH, "../eplus_sim/proposed/")
baseline_model_name = "baseline_model"
proposed_model_name = "proposed_model"

print("########################## Generate RMDs from baseline simulation folder...")
generate_rmd(baseline_dir + baseline_model_name + ".epJSON", baseline_model_name + ".rmd")
print("########################## Generate RMDs from proposed simulation folder...")
generate_rmd(proposed_dir + proposed_model_name + ".epJSON", proposed_model_name + ".rmd")

baseline_rmd_dir = os.path.abspath(baseline_dir + baseline_model_name + ".rmd")
proposed_rmd_dir = os.path.abspath(proposed_dir + proposed_model_name + ".rmd")

# print("########################## Inserting compliance data into both RMDs...")
# replace_lighting_space(baseline_rmd_dir)
# replace_lighting_space(proposed_rmd_dir)

# Change working directory to RCT tool
print("########################## RCT tool checking the RMDs...")
subprocess.run(["pipenv", "run", "rct229", "evaluate", f"{RCT_DIR}/examples/user_rmr.json", baseline_rmd_dir, proposed_rmd_dir], cwd=RCT_DIR, shell=True)
