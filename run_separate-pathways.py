import json
from pathlib import Path

import pandas as pd

import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary

#Run Chemelot pathways
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030_pathways"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Pathways/CH_2030"

    config_filepath = Path(casepath) / "ConfigModel.json"
    tech_filepath = Path(casepath) / "2030/node_data/Chemelot/Technologies.json"

    co2tax = ['ref']
    DD = [0]
    pathways_ammonia = {"conventional": ["SteamReformer", "HaberBosch"],
                        "CC": ["SteamReformer_CC", "HaberBosch"],
                        "electric": ["ElectricSMR_m", "WGS_m",  "HaberBosch", "ASU"],
                        "electrolyzer": ["AEC", "HaberBosch", "ASU"],
                        }
    pathways_ethylene = {"conventional": ["NaphthaCracker"],
                        "CC": ["NaphthaCracker_CC"],
                        "electric": ["NaphthaCracker_Electric"],
                        "methanol1": ["RWGS", "MeOHsynthesis", "MTO"],
                        "methanol2": ["MPW2methanol", "MTO"],
                        "hydrocarbon_upgrading": ["EDH", "PDH"],
                        }
    pathways_auxiliary = ["Boiler_Industrial_NG", "Boiler_El",
                          "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene", "Storage_H2",
                          "Storage_Battery", "Storage_Propylene",
                          "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer",
                          "HBfeed_mixer", "syngas_mixer"]

    for ammonia_key, ammonia_tech in pathways_ammonia.items():
        for ethylene_key, ethylene_tech in pathways_ethylene.items():
            # Combine ammonia, ethylene, and auxiliary pathways
            combined_tech = ammonia_tech + ethylene_tech + pathways_auxiliary

            for tax in co2tax:
                for nr in DD:
                    # change config file
                    with open(config_filepath) as json_file:
                        model_config = json.load(json_file)

                    model_config['optimization']['typicaldays']['N']['value'] = nr
                    model_config['optimization']['objective']['value'] = 'costs'

                    # Write the updated JSON data back to the file
                    with open(config_filepath, 'w') as json_file:
                        json.dump(model_config, json_file, indent=4)

                    # change technologies
                    with open(tech_filepath) as json_file:
                        techs = json.load(json_file)

                    techs["new"] = combined_tech

                    # Write the updated JSON data back to the file
                    with open(tech_filepath, 'w') as json_file:
                        json.dump(techs, json_file, indent=4)

                    # Construct and solve the model
                    pyhub = ModelHub()
                    pyhub.read_data(casepath)

                    if tax == 'high':
                        if nr != 0:
                            pyhub.data.time_series['clustered']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                        pyhub.data.time_series['full']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

                    #add casename based tech combinition
                    pyhub.data.model_config['reporting']['case_name']['value'] = 'a_' + ammonia_key + '_e_' + ethylene_key

                    #solving
                    pyhub.quick_solve()

#Run Chemelot cluster case
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Baseline/CH_2030"
    json_filepath = Path(casepath) / "ConfigModel.json"

    objectives = ['costs']
    # objectives = ['emissions_minC']

    for obj in objectives:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = 20
        model_config['optimization']['objective']['value'] = obj
        model_config['optimization']['emission_limit']['value'] = 0

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        if obj == 'emissions_minC':
            # add casename
            pyhub.data.model_config['reporting']['case_name']['value'] = 'minE_refCO2tax'

            # solving
            pyhub.quick_solve()

        elif obj == 'costs':
            co2tax = ['ref', 'high']

            for tax in co2tax:
                # add casename
                pyhub.data.model_config['reporting']['case_name']['value'] = 'minC_' + tax + 'CO2tax'

                if tax == 'high':
                    pyhub.data.time_series['clustered']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                    pyhub.data.time_series['full']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

                # solving
                pyhub.quick_solve()
