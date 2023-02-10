require 'csv'
require 'openstudio'
# make sure openstudio and openstudio standard are correctly configured
require_relative File.join('..', '..','', 'eplusstd', 'OSSTD_Repo', 'lib','openstudio-standards.rb')

proposed_file_name = "office_med_os"

# Project data shall be the strings copied from:
# make sure climate_zone and epw_file are aligned
climate_zone = 'ASHRAE 169-2013-5A'
epw_file = 'C:\EnergyPlusV9-6-0\WeatherData\USA_CO_Denver-Aurora-Buckley.AFB_.724695_TMY3.epw'
default_hvac_bldg_type = 'other nonresidential'
default_wwr_bldg_type = 'Office 5,000 to 50,000 sq ft'
default_swh_bldg_type = 'Office'

# directory path - DO NOT MODIFY! & DO NOT DELETE source and output folders
prototype_dir = "#{File.dirname(Dir.pwd)}/source"
baseline_dir = "#{File.dirname(Dir.pwd)}/output"

translator = OpenStudio::OSVersion::VersionTranslator.new

########################################################
##### Generate 2019 PRM model ##########################
##### DO NOT MODIFY!!! #################################
########################################################
# Generate baseline
standard = Standard.build("90.1-PRM-2019")
model = translator.loadModel("#{prototype_dir}/office_med_os.osm").get
p "Start generating baseline model... at #{baseline_dir}"

# PRM function inputs

# Load User data
json_path = standard.convert_userdata_csv_to_json("#{File.dirname(Dir.pwd)}/user_data", "#{baseline_dir}")
standard.load_userdata_to_standards_database(json_path)
create_results = standard.model_create_prm_stable_baseline_building(model, climate_zone, default_hvac_bldg_type, default_wwr_bldg_type, default_swh_bldg_type, baseline_dir, unmet_load_hours_check=true, debug=false)

#######################################################
###### Create space data spreadsheet ##################
###### DO NOT MODIFY !!!! #############################
#######################################################
if create_results
  baseline_model = translator.loadModel("#{baseline_dir}/final.osm").get
  CSV.open("#{File.dirname(Dir.pwd)}/output/model_space_name.csv", "w") do |csv|
    csv << ["space_name", "bldg_type", "space_type"]

    model.getThermalZones.each do |zone|
      zone_name = zone.name.get
      space_type = standard.thermal_zone_majority_space_type(zone)
      bt = space_type.get.standardsBuildingType.get unless space_type.get.standardsBuildingType.empty?
      st = space_type.get.standardsSpaceType.get unless space_type.get.standardsSpaceType.empty?
      csv << [zone_name, bt, st]
    end
  end
end
