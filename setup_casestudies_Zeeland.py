import json
import shutil
from pathlib import Path
import adopt_net0.data_preprocessing as dp
from adopt_net0.data_preprocessing.data_loading import find_json_path
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
import pandas as pd

#global functions
read_all_brownfield = 1


#Create data Zeeland cluster short term
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = Path("U:/Data AdOpt-NET0/Model_Linking/Case_Study/ML_Zeeland_bf_2030")
    datapath = Path("U:/Data AdOpt-NET0/Model_Linking/Data/250619_ML_Data_Zeeland_bf")

    firsttime = 0
    if firsttime:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Zeeland"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen",
                         "ammonia", "ethylene", "propylene", "olefins",
                         "crackergas", "feedgas", "steam", "HBfeed", "syngas", "syngas_r",
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

        data['lon'] = 3.81
        data['lat'] = 51.31
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

        # Read climate data
        dp.load_climate_data_from_api(casepath)

    read_techs = 0
    if read_techs or read_all_brownfield:
        set_tecs_new = ["SteamReformer", "ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                        "CrackerFurnace", "CrackerFurnace_Electric", "OlefinSeparation",
                        "ASU", "Boiler_Industrial_NG", "Boiler_El",
                        "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                        "Storage_CO2", "Storage_H2", "Storage_Battery",
                        "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "CO2_mixer", "HBfeed_mixer",
                        "syngas_mixer"]
        set_tecs_existing = {"SteamReformer": 1068, "HaberBosch": 1248, "CrackerFurnace": 451, "OlefinSeparation": 451}

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

                spec_tec_size = {"AEC": 1900, "RWGS": 322, "MeOHsynthesis": 662, "MTO": 993, "SteamReformer": 1269,
                                 "ElectricSMR_m": 2114, "WGS_m": 398, "HaberBosch": 1609, "CrackerFurnace": 535,
                                 "CrackerFurnace_Electric": 892, "OlefinSeparation": 892, "ASU": 112,
                                 "Boiler_Industrial_NG": 3310, "Boiler_El": 1900, "EDH": 688, "PDH": 456,
                                 "MPW2methanol": 305}
                for tec in spec_tec_size.keys():
                    tech_data_file = find_json_path(output_folder, tec)
                    with open(tech_data_file, "r") as json_tecdata_file:
                        tech_data = json.load(json_tecdata_file)

                    tech_data["size_max"] = spec_tec_size[tec]
                    with open(tech_data_file, "w") as json_tecdata_file:
                        json.dump(tech_data, json_tecdata_file, indent=4)

    read_car = 0
    if read_car or read_all_brownfield:
        # Fill carrier data
        dp.fill_carrier_data(casepath, value_or_data=0)

        # Demand data
        dp.fill_carrier_data(casepath, value_or_data=93, columns=['Demand'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=193, columns=['Demand'], carriers=['steam'])
        dp.fill_carrier_data(casepath, value_or_data=42, columns=['Demand'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['feedgas'])

        # Import limits
        dp.fill_carrier_data(casepath, value_or_data=1900, columns=['Import limit'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=7000, columns=['Import limit'],
                             carriers=['methane', 'naphtha', 'methane_bio', 'naphtha_bio', 'ethanol',
                                       'propane', 'CO2_DAC'])

        # Import limit plastic waste
        dp.fill_carrier_data(casepath, value_or_data=469, columns=['Import limit'], carriers=['MPW'])

        # No export limit
        dp.fill_carrier_data(casepath, value_or_data=4000, columns=['Export limit'],
                             carriers=["nitrogen", "steam", "crackergas"])

        # Demand export limit
        dp.fill_carrier_data(casepath, value_or_data=250, columns=['Export limit'],
                             carriers=["ammonia", "ethylene", "propylene"])

        # CO2 export
        dp.fill_carrier_data(casepath, value_or_data=285, columns=['Export limit'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-98.42, columns=['Export price'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Export emission factor'], carriers=['CO2'])

        # Constant import prices
        dp.fill_carrier_data(casepath, value_or_data=56, columns=['Import price'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=141, columns=['Import price'], carriers=['methane_bio'])
        dp.fill_carrier_data(casepath, value_or_data=1830, columns=['Import price'], carriers=['naphtha_bio'])
        dp.fill_carrier_data(casepath, value_or_data=618, columns=['Import price'], carriers=['CO2_DAC'])
        dp.fill_carrier_data(casepath, value_or_data=1734, columns=['Import price'], carriers=['ethanol'])
        dp.fill_carrier_data(casepath, value_or_data=1473, columns=['Import price'], carriers=['propane'])
        dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

        # Constant import emission factor fossil feedstocks
        dp.fill_carrier_data(casepath, value_or_data=0.2, columns=['Import emission factor'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=3.23, columns=['Import emission factor'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=2.38, columns=['Import emission factor'], carriers=['MPW'])

        # Electricity price from file
        json_file_path = casepath / "Topology.json"
        with open(json_file_path, "r") as json_file:
            topology = json.load(json_file)

        for period in topology["investment_periods"]:
            for node_name in topology["nodes"]:
                # load electricity data
                el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_ML.xlsx'
                el_importdata = pd.read_excel(el_load_path, sheet_name=period, header=0, nrows=8760)
                el_price = el_importdata.iloc[:, 1]
                el_emissionrate = el_importdata.iloc[:, 2]

                dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'], carriers=['electricity'])
                dp.fill_carrier_data(casepath, value_or_data=el_emissionrate, columns=['Import emission factor'],
                                     carriers=['electricity'])

                # carbon tax
                file_path = Path(casepath) / period / "node_data" / node_name / 'CarbonCost.csv'
                data = pd.read_csv(file_path, delimiter=';')

                # Set the price to 300 and subsidy to 0 for all rows
                data['price'] = 150.31
                data['subsidy'] = 150.31

                # Save the modified CSV file
                data.to_csv(file_path, index=False, sep=';')


#Create data Zeeland cluster mid term
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = Path("U:/Data AdOpt-NET0/Model_Linking/Case_Study/ML_Zeeland_bf_2040")
    datapath = Path("U:/Data AdOpt-NET0/Model_Linking/Data/250619_ML_Data_Zeeland_bf")

    firsttime = 0
    if firsttime:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Zeeland"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen",
                         "ammonia", "ethylene", "propylene", "olefins",
                         "crackergas", "feedgas", "steam", "HBfeed", "syngas", "syngas_r",
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

        data['lon'] = 3.81
        data['lat'] = 51.31
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

        # Read climate data and fill carried data
        dp.load_climate_data_from_api(casepath)

    read_techs = 1
    if read_techs or read_all_brownfield:
        set_tecs = ["ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                    "CrackerFurnace_Electric",
                    "ASU", "Boiler_Industrial_NG", "Boiler_El",
                    "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                    "DirectMeOHsynthesis", "CO2electrolysis",
                    "Storage_CO2", "Storage_H2", "Storage_Battery",
                    "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "CO2_mixer", "HBfeed_mixer", "syngas_mixer"]
        set_tecs_existing = {}

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
                json_tec['existing'] = set_tecs_existing
                with open(json_tec_file_path, "w") as json_tec_file:
                    json.dump(json_tec, json_tec_file, indent=4)

                # Copy technology and network data into folder
                dp.copy_technology_data(casepath, datapath)

                # Add additional tecs
                output_folder = (
                        casepath / period / "node_data" / node_name / "technology_data"
                )
                set_tecfiles = ["MEA_large", "SteamReformer", "CrackerFurnace", "OlefinSeparation"]
                for tec in set_tecfiles:
                    tec_json_file_path = find_json_path(datapath, tec)
                    if tec_json_file_path:
                        shutil.copy(tec_json_file_path, output_folder)

                spec_tec_size = {"AEC": 3250, "RWGS": 498, "MeOHsynthesis": 812, "MTO": 1195, "SteamReformer": 1269,
                                 "ElectricSMR_m": 2114, "WGS_m": 389, "HaberBosch": 1609, "CrackerFurnace": 535,
                                 "CrackerFurnace_Electric": 892, "OlefinSeparation": 892, "ASU": 112,
                                 "Boiler_Industrial_NG": 3392, "Boiler_El": 3250, "EDH": 688, "PDH": 456,
                                 "MPW2methanol": 344, "DirectMeOHsynthesis": 520, "CO2electrolysis": 283}
                for tec in spec_tec_size.keys():
                    tech_data_file = find_json_path(output_folder, tec)
                    with open(tech_data_file, "r") as json_tecdata_file:
                        tech_data = json.load(json_tecdata_file)

                    tech_data["size_max"] = spec_tec_size[tec]
                    with open(tech_data_file, "w") as json_tecdata_file:
                        json.dump(tech_data, json_tecdata_file, indent=4)

    read_car = 0
    if read_car or read_all_brownfield:
        # Fill carrier data
        dp.fill_carrier_data(casepath, value_or_data=0)

        # Demand data
        dp.fill_carrier_data(casepath, value_or_data=93, columns=['Demand'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=193, columns=['Demand'], carriers=['steam'])
        dp.fill_carrier_data(casepath, value_or_data=42, columns=['Demand'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['feedgas'])

        # Import limits
        dp.fill_carrier_data(casepath, value_or_data=3250, columns=['Import limit'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=7000, columns=['Import limit'],
                             carriers=['methane', 'naphtha', 'methane_bio', 'naphtha_bio', 'ethanol',
                                       'propane', 'MPW', 'CO2_DAC'])

        # Import limit plastic waste
        dp.fill_carrier_data(casepath, value_or_data=529, columns=['Import limit'], carriers=['MPW'])

        # No export limit
        dp.fill_carrier_data(casepath, value_or_data=4000, columns=['Export limit'],
                             carriers=["nitrogen", "steam", "crackergas"])

        # Demand export limit
        dp.fill_carrier_data(casepath, value_or_data=250, columns=['Export limit'],
                             carriers=["ammonia", "ethylene", "propylene"])

        # CO2 export
        dp.fill_carrier_data(casepath, value_or_data=354, columns=['Export limit'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-98.42, columns=['Export price'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Export emission factor'], carriers=['CO2'])

        # Constant import prices
        dp.fill_carrier_data(casepath, value_or_data=56, columns=['Import price'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=141, columns=['Import price'], carriers=['methane_bio'])
        dp.fill_carrier_data(casepath, value_or_data=1830, columns=['Import price'], carriers=['naphtha_bio'])
        dp.fill_carrier_data(casepath, value_or_data=475, columns=['Import price'], carriers=['CO2_DAC'])
        dp.fill_carrier_data(casepath, value_or_data=1734, columns=['Import price'], carriers=['ethanol'])
        dp.fill_carrier_data(casepath, value_or_data=1473, columns=['Import price'], carriers=['propane'])
        dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

        # Constant import emission factor fossil feedstocks
        dp.fill_carrier_data(casepath, value_or_data=0.2, columns=['Import emission factor'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=3.23, columns=['Import emission factor'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=2.38, columns=['Import emission factor'], carriers=['MPW'])

        # Electricity price from file
        json_file_path = casepath / "Topology.json"
        with open(json_file_path, "r") as json_file:
            topology = json.load(json_file)

        for period in topology["investment_periods"]:
            for node_name in topology["nodes"]:
                # load electricity data
                el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_ML.xlsx'
                el_importdata = pd.read_excel(el_load_path, sheet_name=period, header=0, nrows=8760)
                el_price = el_importdata.iloc[:, 1]
                el_emissionrate = el_importdata.iloc[:, 2]

                dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'],
                                     carriers=['electricity'])
                dp.fill_carrier_data(casepath, value_or_data=el_emissionrate,
                                     columns=['Import emission factor'],
                                     carriers=['electricity'])

                #carbon tax
                file_path = Path(casepath) / period / "node_data" / node_name / 'CarbonCost.csv'
                data = pd.read_csv(file_path, delimiter=';')

                # Set the price to 300 and subsidy to 0 for all rows
                data['price'] = 150.31
                data['subsidy'] = 150.31

                # Save the modified CSV file
                data.to_csv(file_path, index=False, sep=';')




#Create data Zeeland cluster long term
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = Path("U:/Data AdOpt-NET0/Model_Linking/Case_Study/ML_Zeeland_bf_2050")
    datapath = Path("U:/Data AdOpt-NET0/Model_Linking/Data/250619_ML_Data_Zeeland_bf")

    firsttime = 0
    if firsttime:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Change topology
        topology_file = casepath / "Topology.json"
        config_file = casepath / "ConfigModel.json"

        topology_template = {
            "nodes": ["Zeeland"],
            "carriers": ["electricity", "methane", "methane_bio", "naphtha", "naphtha_bio",
                         "CO2", "CO2_DAC", "CO2captured", "hydrogen", "nitrogen",
                         "ammonia", "ethylene", "propylene", "olefins",
                         "crackergas", "feedgas", "steam", "HBfeed", "syngas", "syngas_r",
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

        data['lon'] = 3.81
        data['lat'] = 51.31
        data['alt'] = 10

        # Save the modified CSV file
        data.to_csv(file_path, index=False, sep=';')

        # Read climate data and fill carried data
        dp.load_climate_data_from_api(casepath)

    read_techs = 1
    if read_techs or read_all_brownfield:
        set_tecs =["ElectricSMR_m", "WGS_m", "AEC", "HaberBosch",
                    "CrackerFurnace_Electric",
                    "ASU", "Boiler_Industrial_NG", "Boiler_El",
                    "RWGS", "MeOHsynthesis", "MTO", "EDH", "PDH", "MPW2methanol",
                    "DirectMeOHsynthesis", "CO2electrolysis",
                    "Storage_CO2", "Storage_H2", "Storage_Battery",
                    "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "CO2_mixer", "HBfeed_mixer", "syngas_mixer"]
        set_tecs_existing = {}

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
                json_tec['existing'] = set_tecs_existing

                with open(json_tec_file_path, "w") as json_tec_file:
                    json.dump(json_tec, json_tec_file, indent=4)

                # Copy technology and network data into folder
                dp.copy_technology_data(casepath, datapath)

                # Add additional tecs
                set_tecfiles = ["MEA_large", "SteamReformer", "CrackerFurnace", "OlefinSeparation"]
                output_folder = (
                        casepath / period / "node_data" / node_name / "technology_data"
                )
                for tec in set_tecfiles:
                    tec_json_file_path = find_json_path(datapath, tec)
                    if tec_json_file_path:
                        shutil.copy(tec_json_file_path, output_folder)

                spec_tec_size = {"AEC": 4600, "RWGS": 675, "MeOHsynthesis": 962, "MTO": 1659, "SteamReformer": 1269,
                                 "ElectricSMR_m": 2114, "WGS_m": 389, "HaberBosch": 1609, "CrackerFurnace": 535,
                                 "CrackerFurnace_Electric": 892, "OlefinSeparation": 892, "ASU": 112,
                                 "Boiler_Industrial_NG": 3392, "Boiler_El": 4600, "EDH": 688, "PDH": 456,
                                 "MPW2methanol": 382, "DirectMeOHsynthesis": 707, "CO2electrolysis": 401}
                for tec in spec_tec_size.keys():
                    tech_data_file = find_json_path(output_folder, tec)
                    with open(tech_data_file, "r") as json_tecdata_file:
                        tech_data = json.load(json_tecdata_file)

                    tech_data["size_max"] = spec_tec_size[tec]
                    with open(tech_data_file, "w") as json_tecdata_file:
                        json.dump(tech_data, json_tecdata_file, indent=4)

    read_car = 0
    if read_car or read_all_brownfield:
        # Fill carrier data
        dp.fill_carrier_data(casepath, value_or_data=0)

        # Demand data
        dp.fill_carrier_data(casepath, value_or_data=93, columns=['Demand'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=193, columns=['Demand'], carriers=['steam'])
        dp.fill_carrier_data(casepath, value_or_data=42, columns=['Demand'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=0, columns=['Demand'], carriers=['feedgas'])

        # Import limits
        dp.fill_carrier_data(casepath, value_or_data=4600, columns=['Import limit'], carriers=['electricity'])
        dp.fill_carrier_data(casepath, value_or_data=7000, columns=['Import limit'],
                             carriers=['methane', 'naphtha', 'methane_bio', 'naphtha_bio', 'ethanol',
                                       'propane', 'MPW', 'CO2_DAC'])

        # Import limit plastic waste
        dp.fill_carrier_data(casepath, value_or_data=588, columns=['Import limit'], carriers=['MPW'])

        # No export limit
        dp.fill_carrier_data(casepath, value_or_data=4000, columns=['Export limit'],
                             carriers=["nitrogen", "steam", "crackergas"])

        # Demand export limit
        dp.fill_carrier_data(casepath, value_or_data=250, columns=['Export limit'],
                             carriers=["ammonia", "ethylene", "propylene"])

        # CO2 export
        dp.fill_carrier_data(casepath, value_or_data=742, columns=['Export limit'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-98.42, columns=['Export price'], carriers=['CO2'])
        dp.fill_carrier_data(casepath, value_or_data=-1, columns=['Export emission factor'], carriers=['CO2'])

        # Constant import prices
        dp.fill_carrier_data(casepath, value_or_data=59, columns=['Import price'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=148, columns=['Import price'], carriers=['methane_bio'])
        dp.fill_carrier_data(casepath, value_or_data=1830, columns=['Import price'], carriers=['naphtha_bio'])
        dp.fill_carrier_data(casepath, value_or_data=355, columns=['Import price'], carriers=['CO2_DAC'])
        dp.fill_carrier_data(casepath, value_or_data=1734, columns=['Import price'], carriers=['ethanol'])
        dp.fill_carrier_data(casepath, value_or_data=1473, columns=['Import price'], carriers=['propane'])
        dp.fill_carrier_data(casepath, value_or_data=780, columns=['Import price'], carriers=['MPW'])

        # Constant import emission factor fossil feedstocks
        dp.fill_carrier_data(casepath, value_or_data=0.2, columns=['Import emission factor'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=3.23, columns=['Import emission factor'], carriers=['naphtha'])
        dp.fill_carrier_data(casepath, value_or_data=2.38, columns=['Import emission factor'], carriers=['MPW'])

        # Electricity price from file:
        json_file_path = casepath / "Topology.json"
        with open(json_file_path, "r") as json_file:
            topology = json.load(json_file)

        for period in topology["investment_periods"]:
            for node_name in topology["nodes"]:
                # load electricity data
                el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_ML.xlsx'
                el_importdata = pd.read_excel(el_load_path, sheet_name=period, header=0, nrows=8760)
                el_price = el_importdata.iloc[:, 1]
                el_emissionrate = el_importdata.iloc[:, 2]

                dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'],
                                     carriers=['electricity'])
                dp.fill_carrier_data(casepath, value_or_data=el_emissionrate,
                                     columns=['Import emission factor'],
                                     carriers=['electricity'])

                # carbon tax
                file_path = Path(casepath) / period / "node_data" / node_name / 'CarbonCost.csv'
                data = pd.read_csv(file_path, delimiter=';')

                # Set the price to 400 and subsidy to 0 for all rows
                data['price'] = 150.31
                data['subsidy'] = 150.31

                # Save the modified CSV file
                data.to_csv(file_path, index=False, sep=';')

