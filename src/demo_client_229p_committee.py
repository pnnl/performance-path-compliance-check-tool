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

## Weather file directory
WEA_PATH = "C:\\EnergyPlusV9-6-0\\WeatherData\\USA_FL_Tampa.Intl.AP.722110_TMY3.epw"
## EnergyPlus directory (has to be 22.2 or higher)
EPLUS_DIR = "C:\\EnergyPlusV22-2-0\\"
FILE_PATH = os.path.dirname(__file__)

def generate_rmd(input_path, model_name):
	translator = Translator(Path(input_path), model_name)
	translator.process()

# Move the generated baseline IDF and proposed IDF to the target folder
print("########################### Prepare models for simulation #############################")
space_name_csv = os.path.join(FILE_PATH, "../output/model_space_name.csv")
target_proposed_path = os.path.join(FILE_PATH, "../eplus_sim/proposed/proposed_model.idf")
target_baseline_path = os.path.join(FILE_PATH, "../eplus_sim/baseline/baseline_model.idf")
baseline_dir = os.path.join(FILE_PATH, "../eplus_sim/baseline/")
proposed_dir = os.path.join(FILE_PATH, "../eplus_sim/proposed/")
baseline_model_name = "baseline_model"
proposed_model_name = "proposed_model"


# Run Simulation
print("######################################### Running simulations")
run(WEA_PATH, target_proposed_path, "proposed_modelout")
run(WEA_PATH, target_baseline_path, "baseline_modelout")

# Convert IDFs to epJSON
subprocess.run(["ConvertInputFormat", target_proposed_path], cwd=EPLUS_DIR, shell=True)
subprocess.run(["ConvertInputFormat", target_baseline_path], cwd=EPLUS_DIR, shell=True)

# Generates RMDs
# createRulesetModelDescription - developed by GARD Analytics. 
# URL: https://github.com/JasonGlazer/createRulesetModelDescription
print("########################## Generate RMDs from baseline simulation folder...")
generate_rmd(baseline_dir + baseline_model_name + ".epJSON", baseline_model_name + ".rmd")
print("########################## Generate RMDs from proposed simulation folder...")
generate_rmd(proposed_dir + proposed_model_name + ".epJSON", proposed_model_name + ".rmd")
