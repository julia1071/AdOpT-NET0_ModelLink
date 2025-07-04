import os
import sys
from pathlib import Path
import json
from datetime import datetime

from run_aimms_on_python import run_IESA_change_name_files
from extract_data_IESA_multiple_headers import extract_data_IESA_multiple
from run_Zeeland import run_Zeeland
from get_results_cluster_dict_output import extract_technology_outputs
from extract_cc_fractions import extract_cc_fractions
from split_technologies_cc import apply_cc_splitting
from merge_existing_new_techs import merge_existing_and_new_techs
from combine_tech_outputs import combine_tech_outputs
from extract_import_share_naphtha import extract_import_bio_ratios_naphtha
from split_technologies_bio import apply_bio_splitting
from map_techs_to_ID import map_techs_to_ID
from update_input_file_IESA import update_input_file_IESA
from clear_input_file_IESA import clear_input_file_IESA
from compare_outputs import compare_outputs

# Configuration for the function run_IESA_change_name_files

run_from_server = 1

if run_from_server:
    aimms_path = "C:\\Program Files (x86)\\AIMMS\\IFA\\Aimms\\25.3.4.2-x64-VS2022\\Bin\\aimms.exe"
else:
    aimms_path = "C:\\Program Files\\Aimms-25.3.4.2-x64-VS2022.exe"  # Path on your local computer

fast_run = True  # fast optimization of the cluster model for a shorter period (default 10h) to test the model

# Case study choice
linking_energy_prices = True
linking_MPW = False

# Define the file path to the model and the procedures that you want to run,.
command = [
        aimms_path,
        "U:\\IESA-Opt-Dev_20250605_linking_correct\\ModelLinking.aimms", "--end-user",
        "--run-only", "Run_IESA"
    ]

# Pick the file path where AIMMS is saving the results of the optimization.
# The name of the initial results document can be adjusted in AIMMS "Settings_Solve_Transition".
file_path_IESA = Path("U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking")

# The input file name can be changed in AIMMS right clicking on the procedure "runDataReading" selecting attributes
original_name_input = file_path_IESA / "20250619_detailed_linked.xlsx"
original_name_output = file_path_IESA / "ResultsModelLinking_General.xlsx"

# Define the new name of the input and output file
output_basename = "ResultsModelLinking_General_Iteration_"
input_basename = "Input_Iteration_"

# Partly stiff and flexible P/E ratio, base on maximum demand propylene in IESA-Opt.
carrier_demand_dict = {'ethylene': 524400, 'propylene': 235600, 'PE_olefin': 957310, 'ammonia': 1184000}

# Configuration for the function extract_data_IESA

if linking_energy_prices and not linking_MPW:
    # Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
    intervals = ['2030', '2040', '2050']
    list_sheets = ['EnergyCosts']

    nrows = [45]  # !Same order as list_sheets! =Number of rows in excel sheet -1

    # !Combine the headers and filters of the different sheets! Same order as list_sheets!
    headers = ['Activity']
    filters = [['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass']]
elif linking_MPW and not linking_energy_prices:  # Example of other use case: import limit MPW
    intervals = ['2030', '2040', '2050']
    list_sheets = ["SupplyDemand"]
    headers = [("Activity", "Type", "Tech_ID")]
    # Add all the possible technologies that can potentially supply MPW
    filters = [[("Mixed Plastic Waste", "supply", "WAI01_01"), ("Mixed Plastic Waste", "supply", "WAI01_02"),
                ("Mixed Plastic Waste", "supply", "EPO01_03")]]
    nrows = [830]
elif linking_energy_prices and linking_MPW:
    intervals = ['2030', '2040', '2050']
    list_sheets = ['EnergyCosts', 'SupplyDemand']
    nrows = [45, 830]
    headers = [
        'Activity',
        ("Activity", "Type", "Tech_ID")
    ]
    filters = [
        ['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass'],
        [
            ("Mixed Plastic Waste", "supply", "WAI01_01"),
            ("Mixed Plastic Waste", "supply", "WAI01_02"),
            ("Mixed Plastic Waste", "supply", "EPO01_03")
        ]
    ]
else:
    print("Case study not defined, model linking stops")
    sys.exit()

# Define the location and the casepath and the result folder path for the cluster model
casepath = "U:/Data AdOpt-NET0/Model_Linking/Case_Study/ML_Zeeland_bf_"
result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
location = "Zeeland"
# Configuration run Zeeland brownfield case
ppi_file_path = "U:\\Producer_Price_Index_CBS.xlsx"

# Economic base years in the two models.
baseyear_cluster = 2022
baseyear_IESA = 2019

# The alias name (can be anything), the name of the tech in the cluster model,
# and the name of the type of value that you want to extract from cluster results.
base_tech_output_map = {
    "CrackerFurnace": ("CrackerFurnace", "olefins_output"),
    "CrackerFurnace_Electric": ("CrackerFurnace_Electric", "olefins_output"),
    "EDH": ("EDH", "ethylene_output"),
    "MTO": ("MTO", "propylene_output"),
    "PDH": ("PDH", "propylene_output"),
    "MPW2methanol_input": ("MPW2methanol", "MPW_input"),
    "MPW2methanol_output": ("MPW2methanol", "methanol_output"),
    "MeOHsynthesis": ("MeOHsynthesis", "methanol_output"),
    "BiomassGasification": ("BiomassGasification", "methanol_output"),
    "DirectMeOHsynthesis": ("DirectMeOHsynthesis", "methanol_output"),
    "SteamReformer": ("SteamReformer", "HBfeed_output"),
    "AEC": ("AEC", "hydrogen_output"),
    "ElectricSMR_m": ("ElectricSMR_m", "syngas_r_output"),
    "CO2electrolysis": ("CO2electrolysis", "ethylene_output")
}

# Optionally, different outputs as defined above can be combined into one technology
# Such that this combined value is putted into IESA-Opt
group_map = {
    "methanol_from_syngas": [
        "MPW2methanol_output",
        "MeOHsynthesis",
        "BiomassGasification"
    ]
}

capture_rate = 0.9  # The capture rate of the carbon capture technology
# Create a dictionary stating which technologies are splitted in CC and non CC
cc_technologies = {
    "CrackerFurnace": "CrackerFurnace",
    "SteamReformer": "SteamReformer",
    "MPW2methanol_input": "MPW2methanol"
}

# Create a dictionary stating which technologies are splitted in bio and non bio
bio_tech_names = ["CrackerFurnace_CC", "CrackerFurnace_Electric"]

# Create the dictionary where is stated which technology belongs to which Tech_ID.
# More Tech_IDs can be coupled to one name "PDH" : [Tech_ID1, Tech_ID2]
tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03",
              "CrackerFurnace_Electric": "ICH01_05", "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11",
              "MTO": "ICH01_12", "PDH": "ICH01_14", "MPW2methanol_input": "WAI01_10", "MPW2methanol_input_CC": "WAI01_11",
              "methanol_from_syngas": "RFS04_01", "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01",
              "SteamReformer_CC": "Amm01_02", "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08",
              "CO2electrolysis": "ICH01_40"
              }

# Excel must be installed on the server.
input_path = "U:/IESA-Opt-Dev_20250605_linking_correct/data/20250619_detailed_linked.xlsx"

# Convergence Criteria; the relative change in output for each technology in the cluster model must be lower than e
e = 0.1
max_iterations = 3


def model_linking(max_iterations, e):
    i = 1
    inputs_cluster = {}
    outputs_cluster = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H_%M")
    map_name_cluster = result_folder / f"Results_model_linking_{timestamp}"
    map_name_IESA = file_path_IESA / f"Results_model_linking_simplified_{timestamp}"
    os.makedirs(map_name_cluster, exist_ok=True)
    os.makedirs(map_name_IESA, exist_ok=True)
    while True:
        results_path_IESA = run_IESA_change_name_files(i, command, original_name_output, original_name_input,
                                                       output_basename, input_basename, map_name_IESA)
        results_year_sheet = extract_data_IESA_multiple(intervals, list_sheets, nrows, filters, headers,
                                                        results_path_IESA)
        iteration_path = map_name_cluster / f"Iteration_{i}"
        input_cluster = run_Zeeland(results_path_IESA, casepath, iteration_path, location, linking_energy_prices,
                                    linking_MPW, fast_run, results_year_sheet, ppi_file_path, baseyear_cluster,
                                    baseyear_IESA, intervals, carrier_demand_dict)
        tech_output_dict = extract_technology_outputs(base_tech_output_map, iteration_path, intervals, location,
                                                      fast_run)
        print(r"The tech_size_dict created:")
        print(tech_output_dict)
        cc_fraction_dict = extract_cc_fractions(iteration_path, intervals, location, cc_technologies)
        updated_dict_cc = apply_cc_splitting(tech_output_dict, cc_fraction_dict, capture_rate)
        print(r"The updated_dict_cc created:")
        print(updated_dict_cc)
        merged_tech_output_dict = merge_existing_and_new_techs(updated_dict_cc, intervals, location)
        print(r"The merged_tech_output_dict created:")
        print(merged_tech_output_dict)
        combined_dict = combine_tech_outputs(merged_tech_output_dict, group_map)
        bio_ratios = extract_import_bio_ratios_naphtha(iteration_path, intervals, location)
        updated_dict_bio = apply_bio_splitting(combined_dict, bio_ratios, bio_tech_names, location)
        print(r"The updated_dict_bio created:")
        print(updated_dict_bio)
        updates = map_techs_to_ID(updated_dict_bio, tech_to_id)
        print(r"The following updates are inserted into IESA-Opt:")
        print(updates)

        outputs_cluster[f"iteration_{i}"] = updates
        inputs_cluster[f"iteration_{i}"] = input_cluster

        if compare_outputs(outputs_cluster, i, e) or i == max_iterations:
            print(f"✅ Model linking is done after {i} iterations.")

            # Save outputs_cluster to JSON
            output_file = map_name_cluster / "outputs_cluster.json"
            input_file = map_name_cluster / "inputs_cluster.json"

            with open(input_file, "w") as f:
                json.dump(inputs_cluster, f, indent=4)

            with open(output_file, "w") as f:
                json.dump(outputs_cluster, f, indent=4)

            print(f"📝 Saved inputs and outputs of the cluster model")

            clear_input_file_IESA(
                input_path,
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                tech_to_id=tech_to_id
                )
            break  # ← loop ends here
        else:
            update_input_file_IESA(
                input_path,
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                update_data=updates,
                tech_to_id=tech_to_id
            )
            print(f"Linking iteration {i} is executed")
            i += 1
            print(f"The next iteration, iteration {i} is started")


model_linking(max_iterations)
