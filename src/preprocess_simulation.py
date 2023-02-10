#### THIS CODE IS TOXIC AND DO NOT USE IN ANY OTHER PLACES
import subprocess
import csv
import shutil
from user_data_reader import space_to_ltg_type_map
EPLUS_VERSION_UPGRADER_PATH = "C:\\EnergyPlusV22-2-0\\PreProcess\\IDFVersionUpdater\\"
LATEST_VERSION = "V22-2-0"
UPGRADER_MAP = {
	"V9-5-0": "V9-6-0",
	"V9-6-0": "V22-1-0",
	"V22-1-0": "V22-2-0"
}

OSSTD_SPACE_TYPE_901_LIGHTING_TYPE = {
  "WholeBuilding - Lg Office": "OFFICE_OPEN_PLAN",
  "OfficeLarge Main Data Center": "STORAGE_ROOM_LARGE",
  "OfficeLarge Data Center": "STORAGE_ROOM_SMALL",
  "WholeBuilding - Sm Office": "OFFICE_OPEN_PLAN",
}

OSSTD_SPACE_TYPE_901_VENTILATION_TYPE = {
  "WholeBuilding - Lg Office": "OFFICE_BUILDINGS_OFFICE_SPACE",
  "WholeBuilding - Sm Office": "OFFICE_BUILDINGS_OFFICE_SPACE",
  "OfficeLarge Main Data Center": "OFFICE_BUILDINGS_OCCUPIABLE_STORAGE_ROOMS_FOR_DRY_MATERIALS",
  "OfficeLarge Data Center": "OFFICE_BUILDINGS_OCCUPIABLE_STORAGE_ROOMS_FOR_DRY_MATERIALS",
}

OSSTD_SPACE_TYPE_901_SHW_TYPE = {
  "WholeBuilding - Lg Office": "OFFICE",
  "OfficeLarge Main Data Center": "ALL_OTHERS",
  "OfficeLarge Data Center": "ALL_OTHERS",
  "WholeBuilding - Sm Office": "OFFICE",
}


INPUT_INSERT = """
  Output:JSON,
    TimeSeriesAndTabular,    !- Option Type
    Yes,                     !- Output JSON
    No,                      !- Output CBOR
    No;                      !- Output MessagePack

  Output:Variable,
    *,
    schedule value,
    hourly;

  Output:Schedules,
    Hourly;

 OutputControl:Table:Style,
   HTML,            !- Column Separator
   None;            !- Unit Conversion

  Output:Table:SummaryReports,
    AllSummaryAndMonthly;              !- Report 1 Name
"""

SPACE_DATA_TEMPLATE = """
Space,
  %s,   !- Name
  %s,   !- Zone Name
  autocalculate, !- Ceiling Height
  autocalculate, !- Volume
  autocalculate, !- Floor Area {m2}
  %s,   !- Space Type
  %s,   !- Tag 1
  %s;   !- Tag 2
"""

REMOVE_LIST = ["Output:Variable,", "OutputControl:Table:Style,", "Output:Table:SummaryReports,"]


def version_upgrader(curr_ver, model_path):
	if curr_ver == LATEST_VERSION:
		return True
	else:
		transition_app = f"Transition-{curr_ver}-to-{UPGRADER_MAP[curr_ver]}.exe"
		subprocess.run([transition_app, model_path], cwd=EPLUS_VERSION_UPGRADER_PATH, shell=True)
		return version_upgrader(UPGRADER_MAP[curr_ver], model_path)


def modify_idfs_for_rmd(model_path, space_name_csv):
    with open(model_path, 'r') as old_model, open(space_name_csv, 'r') as spaces, open('new_model', 'w') as new_model:
        in_block = False
        for line in old_model:
            temp_line = line.strip()
            if start_with_keys(temp_line):
                print(temp_line)
                in_block = True

            if not in_block:
                new_model.write(line)

            if end_a_block(temp_line):
                print(temp_line)
                in_block = False
        new_model.write(INPUT_INSERT)
        csv_reader = csv.reader(spaces, delimiter=',')
        line_count = 0
        for row in csv_reader:
          if line_count > 0:
            new_model.write(map_osstd_space_data_to_space_template(row))
          line_count += 1
    shutil.move('new_model', model_path)

def start_with_keys(line):
	for key in REMOVE_LIST:
		if line.startswith(key):
			return True
	return False

def end_a_block(line):
	return ";" in line

def map_osstd_space_data_to_space_template(osstd_space):
  """
  osstd_space:
  space_name
  bldg_type
  space_type

  """
  space_data = ""
  if osstd_space[2] != "Plenum" and osstd_space[2] != "Attic":
    space_data = SPACE_DATA_TEMPLATE % (f"{osstd_space[0]}_space", osstd_space[0], OSSTD_SPACE_TYPE_901_LIGHTING_TYPE[osstd_space[2]], OSSTD_SPACE_TYPE_901_VENTILATION_TYPE[osstd_space[2]], OSSTD_SPACE_TYPE_901_SHW_TYPE[osstd_space[2]])
  return space_data

