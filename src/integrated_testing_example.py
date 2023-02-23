import os
import json

from add_baseline_hvac_to_rmd import *


FILE_PATH = os.path.dirname(__file__)

## RCT directory
RCT_DIR = "C:\\git\\ruleset-checking-tool\\"

# Inputs
#system_name = "System_1_PTAC"
system_name = "System_7_VAV_HW_Reheat"
#system_name = "System_4_PSZ_HP"

output_dir = os.path.join(FILE_PATH, "integrated_testing_rmds")

## Define path to System Type
system_type_file = open (
    f"{RCT_DIR}rct229\\ruletest_engine\\ruletest_jsons\\system_types\\{system_name}.json")

# Get system RMD
system_rmd = json.load(system_type_file)

# Get RMDs to inject
seed_rmd_dir = os.path.join(FILE_PATH, "../eplus_sim/proposed/")
proposed_rmd_name = "proposed_model"
proposed_rmd_path = os.path.abspath(seed_rmd_dir + proposed_rmd_name + ".rmd")

rmd_file = open(proposed_rmd_path)

proposed_rmd = json.load(rmd_file)

seed_rmd_dir = os.path.join(FILE_PATH, "../eplus_sim/baseline/")
baseline_rmd_name = "baseline_model"
baseline_rmd_path = os.path.abspath(seed_rmd_dir + baseline_rmd_name + ".rmd")

rmd_file = open(baseline_rmd_path)

baseline_rmd = json.load(rmd_file)


# Add HVAC Systems to
add_hvac_system_to_rmd(proposed_rmd, system_rmd, proposed_rmd_name, system_name, output_dir)
add_hvac_system_to_rmd(baseline_rmd, system_rmd, baseline_rmd_name, system_name, output_dir)


#---------------------------

import subprocess

user_path = os.path.join(output_dir, f"{proposed_rmd_name}_{system_name}.rmd")
proposed_path = os.path.join(output_dir,f"{proposed_rmd_name}_{system_name}.rmd")
baseline_path = os.path.join(output_dir,f"{baseline_rmd_name}_{system_name}.rmd")


subprocess.run(["pipenv", "run", "rct229", "evaluate", user_path, baseline_path, proposed_path], cwd=RCT_DIR, shell=True)