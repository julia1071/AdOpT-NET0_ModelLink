import sys
from pathlib import Path

# === Model settings ==
# # Convergence Criteria; the relative change in output for each technology in the cluster model must be lower than e
e = 0.1
max_iterations = 3
fast_run = True  # fast optimization of the cluster model for a shorter period (default 10h) to test the model

# Case study choice
linking_energy_prices = True
linking_MPW = False

#General data
intervals = ['2030', '2040', '2050']
location = "Zeeland"


# === Paths ===
#IESA paths
if fast_run:
    IESA_path = Path("Z:/IESA-Opt/IESA-Opt-Dev_testing")
    IESA_modellink_path = IESA_path / "20250702_IESA_testing.aimms"
else:
    IESA_path = Path("Z:/IESA-Opt/IESA-Opt-Dev_testing")
    IESA_modellink_path = IESA_path / "20250702_IESA_testing.aimms"

IESA_input_data_path = IESA_path / "data/20250701_detailed_linked.xlsx"
IESA_result_folder = IESA_path / "Output" / "ResultsModelLinking"

#Cluster paths
cluster_case_path = "Z:/AdOpt_NET0/AdOpt_casestudies/Model_Linking/Full/ML_Zeeland_bf_"
cluster_result_folder = Path("Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full")

#Other
ppi_file_path = "Z:/IESA-Opt/Producer_Price_Index_CBS.xlsx"

# Original and new filenames for IESA input and output folders
original_filename_input_IESA = IESA_result_folder / "20250701_detailed_linked.xlsx"
original_filename_output_IESA = IESA_result_folder / "ResultsModelLinking_General.xlsx"

# Define the new name of the input and output file
basename_new_output_IESA = "ResultsModelLinking_General_Iteration_"
basename_new_input_IESA = "Input_Iteration_"


# === AIMMS Paths ===
run_from_server = 0
if run_from_server:
    aimms_path = "C:/Program Files (x86)/AIMMS/IFA/Aimms/25.3.4.2-x64-VS2022/Bin/aimms.exe"
else:
    aimms_path = "C:/Users/5637635/AppData/Local/AIMMS/IFA/Aimms/25.4.4.5-x64-VS2022/Bin/aimms.exe"  # Path on your local computer


# Define the file path to the model and the procedures that you want to run,.
command = [
        aimms_path,
        IESA_modellink_path,
        "--end-user",
        "--run-only",
        "Run_IESA"
    ]

# Economic base years in the two models.
baseyear_cluster = 2022
baseyear_IESA = 2019

# Partly stiff and flexible P/E ratio, base on maximum demand propylene in IESA-Opt.
carrier_demand_dict = {'ethylene': 524400, 'propylene': 235600, 'PE_olefin': 957310, 'ammonia': 1184000}

if linking_energy_prices and not linking_MPW:
    # Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
    list_sheets = ['EnergyCosts', 'EnergyCosts_secondary']

    nrows = [45, 10]  # !Same order as list_sheets! =Number of rows in excel sheet -1

    # !Combine the headers and filters of the different sheets! Same order as list_sheets!
    headers = ['Activity', 'Activity']
    filters = [['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass', 'Bio LPG', 'Bio Ethanol'], ['Mixed Plastic Waste']]
elif linking_MPW and not linking_energy_prices:  # Example of other use case: import limit MPW
    list_sheets = ["SupplyDemand"]
    headers = [("Activity", "Type", "Tech_ID")]
    # Add all the possible technologies that can potentially supply MPW
    filters = [[("Mixed Plastic Waste", "supply", "WAI01_01"), ("Mixed Plastic Waste", "supply", "WAI01_02"),
                ("Mixed Plastic Waste", "supply", "EPO01_03")]]
    nrows = [830]
elif linking_energy_prices and linking_MPW:
    list_sheets = ['EnergyCosts', 'EnergyCosts_secondary', 'SupplyDemand']
    nrows = [45, 10, 830]
    headers = [
        'Activity',
        'Activity',
        ("Activity", "Type", "Tech_ID")
    ]
    filters = [
        ['Naphtha', 'Bio Naphtha', 'Natural Gas HD', 'Biomass', 'Bio LPG', 'Bio Ethanol'],
        ['Mixed Plastic Waste'],
        [
            ("Mixed Plastic Waste", "supply", "WAI01_01"),
            ("Mixed Plastic Waste", "supply", "WAI01_02"),
            ("Mixed Plastic Waste", "supply", "EPO01_03")
        ]
    ]
else:
    print("Case study not defined, model linking stops")
    sys.exit()

# The alias name (can be anything), the name of the tech in the cluster model,
# and the name of the type of value that you want to extract from cluster results.
base_tech_output_map = {
    "CrackerFurnace": ("CrackerFurnace", "olefins"),
    "CrackerFurnace_Electric": ("CrackerFurnace_Electric", "olefins"),
    "EDH": ("EDH", "ethylene"),
    "MTO": ("MTO", "propylene"),
    "PDH": ("PDH", "propylene"),
    "MPW2methanol_input": ("MPW2methanol", "MPW"),
    "MPW2methanol_output": ("MPW2methanol", "methanol"),
    "MeOHsynthesis": ("MeOHsynthesis", "methanol"),
    "Biomass2methanol_input": ("Biomass2methanol", "biomass"),
    "Biomass2methanol_output": ("Biomass2methanol", "methanol"),
    "DirectMeOHsynthesis": ("DirectMeOHsynthesis", "methanol"),
    "SteamReformer": ("SteamReformer", "HBfeed"),
    "AEC": ("AEC", "hydrogen"),
    "ElectricSMR_m": ("ElectricSMR_m", "syngas_r"),
    "CO2electrolysis": ("CO2electrolysis", "ethylene")
}

# Optionally, different outputs as defined above can be combined into one technology
# Such that this combined value is putted into IESA-Opt
group_map = {
    "methanol_from_syngas": [
        "MPW2methanol_output",
        "MeOHsynthesis",
        "Biomass2methanol_output"
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
bio_carriers = ['naphtha']

# Create the dictionary where is stated which technology belongs to which Tech_ID.
# More Tech_IDs can be coupled to one name "PDH" : [Tech_ID1, Tech_ID2]
tech_to_id = {"CrackerFurnace": "ICH01_01",
              "CrackerFurnace_CC": "ICH01_02",
              "CrackerFurnace_CC_bio": "ICH01_03",
              "CrackerFurnace_Electric": "ICH01_05",
              "CrackerFurnace_Electric_bio": "ICH01_06",
              "EDH": "ICH01_11",
              "MTO": "ICH01_12",
              "PDH": "ICH01_41",
              "MPW2methanol_input": "WAI01_10",
              "MPW2methanol_input_CC": "WAI01_11",
              "methanol_from_syngas": "RFS04_01",
              "DirectMeOHsynthesis": "RFS04_02",
              "SteamReformer": "Amm01_01",
              "SteamReformer_CC": "Amm01_02",
              "AEC": "Amm01_05",
              "ElectricSMR_m": "Amm01_08",
              "CO2electrolysis": "ICH01_40",
              "Biomass2methanol_input": "RFS03_01"
              }
