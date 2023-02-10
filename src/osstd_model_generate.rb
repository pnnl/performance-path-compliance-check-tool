require 'csv'
require 'openstudio'
# make sure openstudio and openstudio standard are correctly configured
require_relative File.join('..', '..','', 'eplusstd', 'OSSTD_Repo', 'lib','openstudio-standards.rb')

proposed_file_name = "proposed_model"

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

# directory path - DO NOT MODIFY! & DO NOT DELETE source and output folders
prototype_dir = "#{File.dirname(Dir.pwd)}/source"
baseline_dir = "#{File.dirname(Dir.pwd)}/output"

########################################################
##### Create prototype model based on project data #####
##### DO NOT MODIFY!!! #################################
########################################################
standard = Standard.build("#{code_version}_#{bldg_type}")
model = standard.model_create_prototype_model(climate_zone, epw_file, prototype_dir)

########################################################
### Add code to modify the prototype model #############
########################################################
# Change WWR to 60%
# model.getSurfaces.each do |ss|
# unless ss.subSurfaces.empty?
#   orig_construction = ss.subSurfaces[0].construction.get
#   ss.subSurfaces.sort.each(&:remove)
   # 60% window to wall ratio
#   new_window = ss.setWindowToWallRatio(0.6, 0.8, true).get
#   new_window.setConstruction(orig_construction)
# end
# end

########################################################
##### Save prototype OSM file ##########################
##### DO NOT MODIFY!!! #################################
########################################################
# Save prototype OSM file
osm_path = OpenStudio::Path.new("#{prototype_dir}/#{proposed_file_name}.osm")
# Will need to remove electric transformers.
model.getElectricLoadCenterTransformers.each(&:remove)
standard.model_remove_prm_ems_objects(model)
model.save(osm_path, true)
# Save building model in IDF
forward_translator = OpenStudio::EnergyPlus::ForwardTranslator.new
idf_path = OpenStudio::Path.new("#{prototype_dir}/#{proposed_file_name}.idf")
idf = forward_translator.translateModel(model)
idf.save(idf_path, true)

p "Successfully generated small office model, saved as #{proposed_file_name}.idf"

########################################################
##### Generate 2019 PRM model ##########################
##### DO NOT MODIFY!!! #################################
########################################################
# Generate baseline
standard = Standard.build("90.1-PRM-2019")

p "Start generating baseline model... at #{baseline_dir}"

# PRM function inputs

# Load User data
json_path = standard.convert_userdata_csv_to_json("#{File.dirname(Dir.pwd)}/user_data", "#{baseline_dir}")
standard.load_userdata_to_standards_database(json_path)
create_results = standard.model_create_prm_stable_baseline_building(model, climate_zone, default_hvac_bldg_type, default_wwr_bldg_type, default_swh_bldg_type, baseline_dir, unmet_load_hours_check=false, debug=false)

#######################################################
###### Create space data spreadsheet ##################
###### DO NOT MODIFY !!!! #############################
#######################################################
if create_results
  translator = OpenStudio::OSVersion::VersionTranslator.new
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
