import json

lpd_space_map = {
	"office - enclosed <= 250 sf": "OFFICE_ENCLOSED",
	"retail mall concourse": "RETAIL_FACILITIES_MALL_CONCOURSE",
	"kitchen": "FOOD_PREPARATION_AREA"
}

user_space_data = json.load(open("../output/user_data_json/userdata_space.json"))["userdata_space"]
user_building_data = json.load(open("../output/user_data_json/userdata_building.json"))["userdata_building"]

BULDING_TYPE_FOR_HVAC = user_building_data[0]["building_type_for_hvac"]
BULDING_TYPE_FOR_SHW = user_building_data[0]["building_type_for_swh"]
BULDING_TYPE_FOR_WWR = user_building_data[0]["building_type_for_wwr"]

space_to_ltg_type_map = {}
for user_space in user_space_data:
	space_to_ltg_type_map[user_space["name"].lower()] = lpd_space_map[user_space["std_ltg_type01"]]


