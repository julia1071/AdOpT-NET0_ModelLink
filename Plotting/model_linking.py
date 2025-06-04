import subprocess
import os
import pandas as pd
import sys
import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing, \
    installed_capacities_existing_from_file
import h5py
from adopt_net0 import extract_datasets_from_h5group
# pip install xlwings
import xlwings as xw
import shutil

from run_aimms_on_python import run_IESA_change_name_files
# Configuration for the function run_IESA_change_name_files

run_from_server=1

if run_from_server:
    aimms_path = "C:\\Program Files (x86)\\AIMMS\\IFA\\Aimms\\25.3.4.2-x64-VS2022\\Bin\\aimms.exe"
else:
    aimms_path = "C:\\Program Files\\Aimms-25.3.4.2-x64-VS2022.exe" #Path on your local computer


# Define the file path to the model and the procedures that you want to run,.
command = [
        aimms_path,
        "U:\\IESA-Opt-ModelLinking\\ModelLinking.aimms", "--end-user",
        "--run-only", "Run_IESA"
    ]

# Pick the file path where AIMMS is saving the results of the optimization.
# The name of the initial results document can be adjusted in AIMMS "Settings_Solve_Transition".
original_name_output = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General.xlsx"

#The input file name can be changed in AIMMS right clicking on the procedure "runDataReading" selecting attributes
#!Make sure that the output folder is empty and does not contain results from a previous run!
original_name_input = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/20250430_detailed.xlsx"

#Define the new name of the input and output file
new_name_output = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General_Iteration_"
new_name_input = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/Input_Iteration_"

from extract_data_IESA import extract_data_IESA, get_value_IESA

# Configuration for the function extract_data_IESA

# Replace 'your_file.xlsx' with the path to your Excel file - this can be linked to the main iteration by including {i+1 in the file name as in "Run AIMMS on Python"}
file_path = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General.xlsx."

#Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
simulation_years=['2030','2040','2050']
list_sheets= ['EnergyCosts','Configuration_Stock']
nrows=[40, 320]#!Same order as list_sheets! =Number of rows in excel sheet -1

#Define the corresponding properties of the sheets and the specific data that you want to extract.
header_energycosts = 'Activity'
filter_energycosts = ['Naphtha', 'Bio Naphtha', 'Bio Ethanol', 'Electricity EU', 'Sugars', 'Manure']

header_stock = 'Tech_ID'
filter_stock = ['RFP02_01', 'WAI01_03']

#!Combine the headers and filters of the different sheets! Same order as list_sheets!
headers = [header_energycosts,header_stock]
filters = [filter_energycosts, filter_stock]

from run_brownfield import run_brownfield

# Configuration run brownfield
execute = 1

from get_results_cluster_dict import extract_data_cluster

# --- Configuration ---
result_folder = Path("U:/Data AdOpt-NET0/Test/Result path/EL_Chemelot")
intervals = ["2030", "2040", "2050"]
location = "Chemelot"

#Create the dictionary where is stated which technology belongs to which Tech_ID. Check these values when really using.
tech_to_id = {"CrackerFurnace_Electric": "ICH01_05",
              "CrackerFurnace_existing": "ICH01_01" ,"EDH_existing": "ICH01_11","HaberBosch_existing": "Amm01_01"}

from update_input_file_IESA import update_input_file_IESA

# Excel must be installed on the server.
# This method is used because the "complicated" Excel input file for IESA-Opt gets corrupted while using openpyxl.

template_path = "U:/IESA-Opt-ModelLinking/data/20250430_detailed - kopie.xlsx" #Create a template (base) input file.
output_path = "U:/IESA-Opt-ModelLinking/data/20250430_detailed.xlsx" #Save the file with a name that is corresponding to the name defined in runDataReading AIMMS

iterations = 2
def model_linking(iterations):
    i = 0
    while i< iterations:
        i += 1
        file_path = run_IESA_change_name_files(i, command, original_name_output, original_name_input, new_name_output, new_name_input)
        results_year_sheet = extract_data_IESA(simulation_years, list_sheets, nrows,filters, headers, file_path)
        run_brownfield(execute, results_year_sheet)
        updates = extract_data_cluster(result_folder,intervals, location, tech_to_id)
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
    print("Linking is executed")

results = model_linking(iterations)
