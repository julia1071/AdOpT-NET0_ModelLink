import json
import shutil
from pathlib import Path
import adopt_net0.data_preprocessing as dp
from adopt_net0.data_preprocessing.data_loading import find_json_path
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
import pandas as pd

#Create data Chemelot cluster short term
execute = 1
linear = 0
greenfield = 0

if execute == 1:
    if linear:
        # Specify the path to your input data
        casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030_linear")
        datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/291018_MY_Data_CH_2030_linear")
    else:
        if greenfield:
            # Specify the path to your input data
            casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_gf_2030")
            datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")
        else:
            # Specify the path to your input data
            casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_2030")
            datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")

    firsttime = 0
    if firsttime == 1:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Chemelot"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen", "oxygen",
                         "ammonia", "ethylene", "propylene", "PE_olefin", "olefins",
                         "crackergas", "feedgas", "steam", "heatlowT", "HBfeed", "syngas", "syngas_r",
                         "methanol", "ethanol", "propane", "MPW"],
            "investment_periods": ["2030"],
            "start_date": "2022-01-01 00:00",
            "end_date": "2022-12-31 23:00",
            "resolution": "1h",
            "investment_period_length": 1,
        }

        # open and save topology and configuration files
        with open(topology_file, "w") as f:
            json.dump(topology_template, f, indent=4)
        # with open(config_file, "w") as f:
        # json.dump(configuration_template, f, indent=4)

        # Create folder structure
        dp.create_input_data_folder_template(casepath)

        # Node location
        file_path = casepath / 'NodeLocations.csv'
        data = pd.read_csv(file_path, delimiter=';')

        data['lon'] = 5.80
        data['lat'] = 50.97
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

    if greenfield:
        set_tecs_new = ["SteamReformer", "ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                    "CrackerFurnace", "CrackerFurnace_Electric", "OlefinSeparation",
                    "ASU", "Boiler_Industrial_NG", "Boiler_El",
                    "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                    "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene",
                    "Storage_H2", "Storage_Battery", "Storage_Propylene",
                    "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer", "HBfeed_mixer", "syngas_mixer"]
    else:
        set_tecs_new = ["ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                        "NaphthaCracker_Electric",
                        "ASU", "Boiler_Industrial_NG", "Boiler_El",
                        "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                        "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene",
                        "Storage_H2", "Storage_Battery", "Storage_Propylene",
                        "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer", "HBfeed_mixer",
                        "syngas_mixer"]
        set_tecs_existing = {"SteamReformer": 1060, "HaberBosch": 805, "CrackerFurnace": 495, "OlefinSeparation": 495}

    json_file_path = casepath / "Topology.json"
    with open(json_file_path, "r") as json_file:
        topology = json.load(json_file)

    for period in topology["investment_periods"]:
        for node_name in topology["nodes"]:
            # Read the JSON technology file
            json_tec_file_path = (
                    casepath / period / "node_data" / node_name / "Technologies.json"
            )
            with open(json_tec_file_path, "r") as json_tec_file:
                json_tec = json.load(json_tec_file)

            json_tec['new'] = set_tecs_new
            if not greenfield:
                json_tec['existing'] = set_tecs_existing
            with open(json_tec_file_path, "w") as json_tec_file:
                json.dump(json_tec, json_tec_file, indent=4)

    # Copy technology and network data into folder
    dp.copy_technology_data(casepath, datapath)
    # Add CCS
    output_folder = (
            casepath / period / "node_data" / node_name / "technology_data"
    )
    tec_json_file_path = find_json_path(datapath, "MEA_large")
    if tec_json_file_path:
        shutil.copy(tec_json_file_path, output_folder)

    # Read climate data and fill carried data
    dp.load_climate_data_from_api(casepath)
    dp.fill_carrier_data(casepath, value_or_data=0)

    # Demand data
    dp.fill_carrier_data(casepath, value_or_data=135, columns=['Demand'], carriers=['ammonia'])
    dp.fill_carrier_data(casepath, value_or_data=44, columns=['Demand'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=218, columns=['Demand'], carriers=['PE_olefin'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['steam'])
    dp.fill_carrier_data(casepath, value_or_data=81.8, columns=['Demand'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=6.9, columns=['Demand'], carriers=['feedgas'])

    # No import limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Import limit'],
                         carriers=["electricity", "methane", "naphtha"])

    # Import limits
    dp.fill_carrier_data(casepath, value_or_data=750, columns=['Import limit'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=2359, columns=['Import limit'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=1648, columns=['Import limit'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=526, columns=['Import limit'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=157, columns=['Import limit'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=1121, columns=['Import limit'], carriers=['MPW'])

    # No export limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Export limit'],
                         carriers=["nitrogen", "oxygen", "steam", "heatlowT"])

    # CO2 export
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Export limit'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=-111.51, columns=['Export price'], carriers=['CO2'])

    # Constant import prices
    dp.fill_carrier_data(casepath, value_or_data=56.45, columns=['Import price'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=127.68, columns=['Import price'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=1852.5, columns=['Import price'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=382.81, columns=['Import price'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=908.20, columns=['Import price'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=1141.07, columns=['Import price'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=1710, columns=['Import price'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

    # Constant import emission factor
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=-0.2, columns=['Import emission factor'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1.32, columns=['Import emission factor'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Import emission factor'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=-1.37, columns=['Import emission factor'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=-1.91, columns=['Import emission factor'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=-2.99, columns=['Import emission factor'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['MPW'])

    # Electricity price from file
    # change to xlsx and read sheet with year 2030
    el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_MY.xlsx'
    el_importdata = pd.read_excel(el_load_path, sheet_name='2030', header=0, nrows=8760)
    el_price = el_importdata.iloc[:, 0]
    el_emissionrate = el_importdata.iloc[:, 2]

    dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=el_emissionrate, columns=['Import emission factor'],
                         carriers=['electricity'])

    #carbon tax
    file_path = Path(casepath) / '2030' / "node_data" / 'Chemelot' / 'CarbonCost.csv'
    data = pd.read_csv(file_path, delimiter=';')

    # Set the price to 150.31 and subsidy to 0 for all rows
    data['price'] = 150.31
    data['subsidy'] = 0

    # Save the modified CSV file
    data.to_csv(file_path, index=False, sep=';')


#Create data Chemelot cluster mid term
execute = 0
greenfield = 0

if execute == 1:
    if greenfield:
        # Specify the path to your input data
        casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_gf_2040")
        datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")
    else:
        # Specify the path to your input data
        casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_2040")
        datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")

    firsttime = 0
    if firsttime == 1:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Chemelot"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen", "oxygen",
                         "ammonia", "ethylene", "propylene", "PE_olefin", "olefins",
                         "crackergas", "feedgas", "steam", "heatlowT", "HBfeed", "syngas", "syngas_r",
                         "methanol", "ethanol", "propane", "MPW"],
            "investment_periods": ["2040"],
            "start_date": "2022-01-01 00:00",
            "end_date": "2022-12-31 23:00",
            "resolution": "1h",
            "investment_period_length": 1,
        }

        # open and save topology and configuration files
        with open(topology_file, "w") as f:
            json.dump(topology_template, f, indent=4)
        # with open(config_file, "w") as f:
        # json.dump(configuration_template, f, indent=4)

        # Create folder structure
        dp.create_input_data_folder_template(casepath)

        # Node location
        file_path = casepath / 'NodeLocations.csv'
        data = pd.read_csv(file_path, delimiter=';')

        data['lon'] = 5.80
        data['lat'] = 50.97
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

    set_tecs = ["SteamReformer", "ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                "CrackerFurnace", "CrackerFurnace_Electric",
                "ASU", "Boiler_Industrial_NG", "Boiler_El",
                "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                "DirectMeOHsynthesis", "CO2electrolysis_2040",
                "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene",
                "Storage_H2", "Storage_Battery", "Storage_Propylene",
                "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer", "HBfeed_mixer", "syngas_mixer"]

    json_file_path = casepath / "Topology.json"
    with open(json_file_path, "r") as json_file:
        topology = json.load(json_file)

    for period in topology["investment_periods"]:
        for node_name in topology["nodes"]:
            # Read the JSON technology file
            json_tec_file_path = (
                    casepath / period / "node_data" / node_name / "Technologies.json"
            )
            with open(json_tec_file_path, "r") as json_tec_file:
                json_tec = json.load(json_tec_file)

            json_tec['new'] = set_tecs
            with open(json_tec_file_path, "w") as json_tec_file:
                json.dump(json_tec, json_tec_file, indent=4)

    # Copy technology and network data into folder
    dp.copy_technology_data(casepath, datapath)
    # Add CCS
    output_folder = (
            casepath / period / "node_data" / node_name / "technology_data"
    )
    tec_json_file_path = find_json_path(datapath, "MEA_large")
    if tec_json_file_path:
        shutil.copy(tec_json_file_path, output_folder)

    # Read climate data and fill carried data
    dp.load_climate_data_from_api(casepath)
    dp.fill_carrier_data(casepath, value_or_data=0)

    # Demand data
    dp.fill_carrier_data(casepath, value_or_data=135, columns=['Demand'], carriers=['ammonia'])
    dp.fill_carrier_data(casepath, value_or_data=44, columns=['Demand'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=218, columns=['Demand'], carriers=['PE_olefin'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['steam'])
    dp.fill_carrier_data(casepath, value_or_data=81.8, columns=['Demand'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=6.9, columns=['Demand'], carriers=['feedgas'])

    # No import limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Import limit'],
                         carriers=["electricity", "methane", "naphtha"])

    # Import limits
    dp.fill_carrier_data(casepath, value_or_data=750, columns=['Import limit'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=2359, columns=['Import limit'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=1648, columns=['Import limit'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=526, columns=['Import limit'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=157, columns=['Import limit'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=1121, columns=['Import limit'], carriers=['MPW'])

    # No export limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Export limit'],
                         carriers=["nitrogen", "oxygen", "steam", "heatlowT"])

    # CO2 export
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Export limit'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=-111.51, columns=['Export price'], carriers=['CO2'])

    # Constant import prices
    dp.fill_carrier_data(casepath, value_or_data=56.45, columns=['Import price'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=127.68, columns=['Import price'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=1852.5, columns=['Import price'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=382.81, columns=['Import price'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=908.20, columns=['Import price'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=1141.07, columns=['Import price'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=1710, columns=['Import price'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

    # Constant import emission factor
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=-0.2, columns=['Import emission factor'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1.32, columns=['Import emission factor'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Import emission factor'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=-1.37, columns=['Import emission factor'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=-1.91, columns=['Import emission factor'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=-2.99, columns=['Import emission factor'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['MPW'])

    # Electricity price from file
    # change to xlsx and read sheet with year 2030
    el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_MY.xlsx'
    el_importdata = pd.read_excel(el_load_path, sheet_name='2040', header=0, nrows=8760)
    el_price = el_importdata.iloc[:, 0]
    el_emissionrate = el_importdata.iloc[:, 2]

    dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=el_emissionrate, columns=['Import emission factor'],
                         carriers=['electricity'])

    #carbon tax
    file_path = Path(casepath) / '2040' / "node_data" / 'Chemelot' / 'CarbonCost.csv'
    data = pd.read_csv(file_path, delimiter=';')

    # Set the price to 150.31 and subsidy to 0 for all rows
    data['price'] = 150.31
    data['subsidy'] = 0

    # Save the modified CSV file
    data.to_csv(file_path, index=False, sep=';')




#Create data Chemelot cluster long term
execute = 0
greenfield = 0

if execute == 1:
    if greenfield:
        # Specify the path to your input data
        casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_gf_2050")
        datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")
    else:
        # Specify the path to your input data
        casepath = Path("Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_2050")
        datapath = Path("Z:/AdOpt_NET0/AdOpt_data/MY/241205_MY_Data_Chemelot")

    firsttime = 0
    if firsttime == 1:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Chemelot"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen", "oxygen",
                         "ammonia", "ethylene", "propylene", "PE_olefin", "olefins",
                         "crackergas", "feedgas", "steam", "heatlowT", "HBfeed", "syngas", "syngas_r",
                         "methanol", "ethanol", "propane", "MPW"],
            "investment_periods": ["2050"],
            "start_date": "2022-01-01 00:00",
            "end_date": "2022-12-31 23:00",
            "resolution": "1h",
            "investment_period_length": 1,
        }

        # open and save topology and configuration files
        with open(topology_file, "w") as f:
            json.dump(topology_template, f, indent=4)
        # with open(config_file, "w") as f:
        # json.dump(configuration_template, f, indent=4)

        # Create folder structure
        dp.create_input_data_folder_template(casepath)

        # Node location
        file_path = casepath / 'NodeLocations.csv'
        data = pd.read_csv(file_path, delimiter=';')

        data['lon'] = 5.80
        data['lat'] = 50.97
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

    set_tecs = ["SteamReformer", "ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                "CrackerFurnace", "CrackerFurnace_Electric",
                "ASU", "Boiler_Industrial_NG", "Boiler_El",
                "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                "DirectMeOHsynthesis", "CO2electrolysis_2040", "CO2electrolysis_2050",
                "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene",
                "Storage_H2", "Storage_Battery", "Storage_Propylene",
                "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer", "HBfeed_mixer", "syngas_mixer"]

    json_file_path = casepath / "Topology.json"
    with open(json_file_path, "r") as json_file:
        topology = json.load(json_file)

    for period in topology["investment_periods"]:
        for node_name in topology["nodes"]:
            # Read the JSON technology file
            json_tec_file_path = (
                    casepath / period / "node_data" / node_name / "Technologies.json"
            )
            with open(json_tec_file_path, "r") as json_tec_file:
                json_tec = json.load(json_tec_file)

            json_tec['new'] = set_tecs
            with open(json_tec_file_path, "w") as json_tec_file:
                json.dump(json_tec, json_tec_file, indent=4)

    # Copy technology and network data into folder
    dp.copy_technology_data(casepath, datapath)
    # Add CCS
    output_folder = (
            casepath / period / "node_data" / node_name / "technology_data"
    )
    tec_json_file_path = find_json_path(datapath, "MEA_large")
    if tec_json_file_path:
        shutil.copy(tec_json_file_path, output_folder)

    # Read climate data and fill carried data
    dp.load_climate_data_from_api(casepath)
    dp.fill_carrier_data(casepath, value_or_data=0)

    # Demand data
    dp.fill_carrier_data(casepath, value_or_data=135, columns=['Demand'], carriers=['ammonia'])
    dp.fill_carrier_data(casepath, value_or_data=44, columns=['Demand'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=218, columns=['Demand'], carriers=['PE_olefin'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['steam'])
    dp.fill_carrier_data(casepath, value_or_data=81.8, columns=['Demand'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=6.9, columns=['Demand'], carriers=['feedgas'])

    # No import limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Import limit'],
                         carriers=["electricity", "methane", "naphtha"])

    # Import limits
    dp.fill_carrier_data(casepath, value_or_data=750, columns=['Import limit'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=2114, columns=['Import limit'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=990, columns=['Import limit'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=2359, columns=['Import limit'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=1648, columns=['Import limit'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=526, columns=['Import limit'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=157, columns=['Import limit'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=1121, columns=['Import limit'], carriers=['MPW'])

    # No export limit
    dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Export limit'],
                         carriers=["nitrogen", "oxygen", "steam", "heatlowT"])

    # CO2 export
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Export limit'], carriers=['CO2'])
    dp.fill_carrier_data(casepath, value_or_data=-111.51, columns=['Export price'], carriers=['CO2'])

    # Constant import prices
    dp.fill_carrier_data(casepath, value_or_data=56.45, columns=['Import price'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=127.68, columns=['Import price'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=1852.5, columns=['Import price'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=382.81, columns=['Import price'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=908.20, columns=['Import price'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=1141.07, columns=['Import price'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=1710, columns=['Import price'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

    # Constant import emission factor
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['methane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['naphtha'])
    dp.fill_carrier_data(casepath, value_or_data=-0.2, columns=['Import emission factor'], carriers=['methane_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1.32, columns=['Import emission factor'], carriers=['naphtha_bio'])
    dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Import emission factor'], carriers=['CO2_DAC'])
    dp.fill_carrier_data(casepath, value_or_data=-1.37, columns=['Import emission factor'], carriers=['methanol'])
    dp.fill_carrier_data(casepath, value_or_data=-1.91, columns=['Import emission factor'], carriers=['ethanol'])
    dp.fill_carrier_data(casepath, value_or_data=-2.99, columns=['Import emission factor'], carriers=['propane'])
    dp.fill_carrier_data(casepath, value_or_data=0, columns=['Import emission factor'], carriers=['MPW'])

    # Electricity price from file
    # change to xlsx and read sheet with year 2030
    el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_MY.xlsx'
    el_importdata = pd.read_excel(el_load_path, sheet_name='2050', header=0, nrows=8760)
    el_price = el_importdata.iloc[:, 0]
    el_emissionrate = el_importdata.iloc[:, 2]

    dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=el_emissionrate, columns=['Import emission factor'],
                         carriers=['electricity'])

    #carbon tax
    file_path = Path(casepath) / '2050' / "node_data" / 'Chemelot' / 'CarbonCost.csv'
    data = pd.read_csv(file_path, delimiter=';')

    # Set the price to 150.31 and subsidy to 0 for all rows
    data['price'] = 150.31
    data['subsidy'] = 0

    # Save the modified CSV file
    data.to_csv(file_path, index=False, sep=';')

