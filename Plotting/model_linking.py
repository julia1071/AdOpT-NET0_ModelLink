
import sys
from pathlib import Path


from run_aimms_on_python import run_IESA_change_name_files
# Configuration for the function run_IESA_change_name_files

run_from_server=1

if run_from_server:
    aimms_path = "C:\\Program Files (x86)\\AIMMS\\IFA\\Aimms\\25.3.4.2-x64-VS2022\\Bin\\aimms.exe"
else:
    aimms_path = "C:\\Program Files\\Aimms-25.3.4.2-x64-VS2022.exe" #Path on your local computer

 # Case study choice
linking_energy_prices = 1
linking_mpw = 0

# Define the file path to the model and the procedures that you want to run,.
command = [
        aimms_path,
        "U:\\IESA-Opt-Dev_20250605_linking_correct\\ModelLinking.aimms", "--end-user",
        "--run-only", "Run_IESA"
    ]

# Pick the file path where AIMMS is saving the results of the optimization.
# The name of the initial results document can be adjusted in AIMMS "Settings_Solve_Transition".
original_name_output = "U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/ResultsModelLinking_General.xlsx"

#The input file name can be changed in AIMMS right clicking on the procedure "runDataReading" selecting attributes
#!Make sure that the output folder is empty and does not contain results from a previous run!
original_name_input = "U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/20250612_detailed_linked.xlsx"

#Define the new name of the input and output file
new_name_output = "U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/ResultsModelLinking_General_Iteration_"
new_name_input = "U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/Input_Iteration_"

from extract_data_IESA import extract_data_IESA, get_value_IESA

# Configuration for the function extract_data_IESA

if linking_energy_prices:
    # Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
    intervals =['2030','2040','2050']
    list_sheets= ['EnergyCosts']

    nrows=[45] # !Same order as list_sheets! =Number of rows in excel sheet -1

    #Define the corresponding properties of the sheets and the specific data that you want to extract.
    header_energycosts = 'Activity'
    filter_energycosts = ['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass']


    # !Combine the headers and filters of the different sheets! Same order as list_sheets!
    headers = [header_energycosts]
    filters = [filter_energycosts]

elif linking_mpw:
    # Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
    intervals =['2030','2040','2050']
    list_sheets= ['SupplyDemand']

    nrows=[45] # !Same order as list_sheets! =Number of rows in excel sheet -1

    #Define the corresponding properties of the sheets and the specific data that you want to extract.
    header_energycosts = 'Activity'
    filter_energycosts = ['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass']

    #header_stock = 'Tech_ID'
    #filter_stock = ['RFP02_01', 'WAI01_03']

    # !Combine the headers and filters of the different sheets! Same order as list_sheets!
    headers = [header_energycosts]
    filters = [filter_energycosts]

else:
    print("Case study not defined, model linking stops")
    sys.exit()


from run_Zeeland import run_Zeeland

# Configuration run Zeeland brownfield case
ppi_file_path = "U:\\Producer_Price_Index_CBS.xlsx"

# Economic base years in the two models.
baseyear_cluster = 2022
baseyear_IESA = 2019

from get_results_cluster_dict import extract_data_cluster

# --- Configuration ---
result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
location = "Zeeland"

from extract_cc_fractions import extract_cc_fractions

from split_technologies_cc import apply_cc_splitting
capture_rate = 0.9 # The capture rate of the carbon capture technology

from merge_existing_new_techs import merge_existing_and_new_techs

from extract_import_share_naphtha import extract_import_bio_ratios_naphtha

from split_technologies_bio import apply_bio_splitting

# Create a dictionary stating which technologies are splitted in bio and non bio
bio_tech_names = ["CrackerFurnace_CC", "CrackerFurnace_Electric"]

from map_techs_to_ID import map_techs_to_ID

# Create the dictionary where is stated which technology belongs to which Tech_ID. Check these values when really using.
tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03", "CrackerFurnace_Electric": "ICH01_05",
              "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11", "MTO": "ICH01_12", "PDH": "ICH01_14", "MPW2methanol": ["WAI01_10","RFS04_01"],
              "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
                "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
              }

from update_input_file_IESA import update_input_file_IESA

# Excel must be installed on the server.
# This method is used because the "complicated" Excel input file for IESA-Opt gets corrupted while using openpyxl.

template_path = "U:/IESA-Opt-Dev_20250605_linking_correct/data/20250612_detailed_linked - initial template.xlsx" # Template input file.
output_path = "U:/IESA-Opt-Dev_20250605_linking_correct/data/20250612_detailed_linked.xlsx" # Save the file with a name that is corresponding to the name defined in runDataReading AIMMS

iterations = 4
def model_linking(iterations):
    i = 0
    while i< iterations:
        i += 1
        results_path_IESA = run_IESA_change_name_files(i, command, original_name_output, original_name_input, new_name_output, new_name_input)
        results_year_sheet = extract_data_IESA(intervals, list_sheets, nrows, filters, headers, results_path_IESA)
        run_Zeeland(linking_energy_prices, linking_mpw, results_year_sheet, ppi_file_path, baseyear_cluster, baseyear_IESA)
        tech_size_dict = extract_data_cluster(result_folder, intervals, location)
        print(r"The tech_size_dict created:")
        print(tech_size_dict)
        cc_fraction_dict = extract_cc_fractions(result_folder, intervals, location)
        updated_dict_cc = apply_cc_splitting(tech_size_dict, cc_fraction_dict, capture_rate)
        print(r"The updated_dict_cc created:")
        print(updated_dict_cc)
        merged_tech_size_dict = merge_existing_and_new_techs(updated_dict_cc, intervals, location)
        print(r"The merged_tech_size_dict created:")
        print(merged_tech_size_dict)
        bio_ratios = extract_import_bio_ratios_naphtha(result_folder, intervals, location)
        updated_dict_bio = apply_bio_splitting(merged_tech_size_dict, bio_ratios, bio_tech_names, location)
        print(r"The updated_dict_bio created:")
        print(updated_dict_bio)
        updates = map_techs_to_ID(updated_dict_bio, tech_to_id)
        print(r"The following updates are inserted into IESA-Opt:")
        print(updates)
        update_input_file_IESA(
            template_path=template_path,
            output_path=output_path,
            sheet_name="Technologies",
            tech_id_col="A",
            tech_id_row_start=7,
            merged_row=2,
            header_row=5,
            merged_name="Minimum use in a year",
            update_data=updates
        )
    print(f"Linking iteration {i} is executed")

model_linking(iterations)
