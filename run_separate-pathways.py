import json
from pathlib import Path
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_technology_sizes_zero

#Run Chemelot pathways
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2040_pathways"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Pathways/CH_2040"

    config_filepath = Path(casepath) / "ConfigModel.json"
    tech_filepath = Path(casepath) / "2030/node_data/Chemelot/Technologies.json"

    co2tax = ['ref']
    DD = [0]
    pathways_ammonia = {"conventional": ["SteamReformer", "HaberBosch"],
                        "CC": ["SteamReformer_CC", "HaberBosch"],
                        "electric": ["ElectricSMR_m", "WGS_m", "HaberBosch", "ASU"],
                        "electrolyzer": ["AEC", "HaberBosch", "ASU"],
                        }
    pathways_ethylene = {"conventional": ["NaphthaCracker"],
                         "CC": ["NaphthaCracker_CC"],
                         "electric": ["NaphthaCracker_Electric"],
                         "methanol1": ["RWGS", "MeOHsynthesis", "MTO"],
                         "methanol2": ["DirectMeOHsynthesis", "MTO"],
                         "methanol3": ["MPW2methanol", "MTO"],
                         "hydrocarbon_upgrading": ["EDH", "PDH"],
                         "CO2electrolysis": ["CO2electrolysis_2040"],
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

                    # change save options
                    model_config['reporting']['save_summary_path']['value'] = resultpath
                    model_config['reporting']['save_path']['value'] = resultpath

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
                            pyhub.data.time_series['clustered'][
                                'period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                        pyhub.data.time_series['full']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

                    #add casename based tech combinition
                    pyhub.data.model_config['reporting']['case_name']['value'] = 'a_' + ammonia_key + '_e_' + ethylene_key

                    #solving
                    pyhub.quick_solve()

#Run Chemelot warmstart
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Pathways/CH_2030_ws"

    config_filepath = Path(casepath) / "ConfigModel.json"

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
    pathways_auxiliary = {"Boiler_Industrial_NG", "Boiler_El",
                          "Storage_Ammonia", "Storage_CO2", "Storage_Ethylene", "Storage_H2",
                          "Storage_Battery", "Storage_Propylene",
                          "CO2toEmission", "feedgas_mixer", "naphtha_mixer", "PE_mixer", "CO2_mixer",
                          "HBfeed_mixer", "syngas_mixer"}

    # Initialize the dictionary, setting all technologies to True
    tech_status = {tech: True for pathway in pathways_ammonia.values() for tech in pathway}
    tech_status.update({tech: True for pathway in pathways_ethylene.values() for tech in pathway})

    # Define the order of pathways to unfix
    unfix_order_pathways = [
        {"ethylene": "conventional", "ammonia": "electric"},
        {"ethylene": "electric", "ammonia": "conventional"},
        {"ethylene": "CC", "ammonia": "CC"},
        {"ammonia": "electrolyzer"},
        {"ethylene": ["methanol1", "methanol2"]},
        {"ethylene": "hydrocarbon_upgrading"}
    ]

    for tax in co2tax:
        for nr in DD:
            # change config file
            with open(config_filepath) as json_file:
                model_config = json.load(json_file)

            model_config['optimization']['typicaldays']['N']['value'] = nr
            model_config['optimization']['objective']['value'] = 'costs'

            # change save options
            model_config['reporting']['save_summary_path']['value'] = resultpath
            model_config['reporting']['save_path']['value'] = resultpath

            # Write the updated JSON data back to the file
            with open(config_filepath, 'w') as json_file:
                json.dump(model_config, json_file, indent=4)

            # Construct and solve the model
            pyhub = ModelHub()
            pyhub.read_data(casepath)

            if tax == 'high':
                if nr != 0:
                    pyhub.data.time_series['clustered'][
                        'period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                pyhub.data.time_series['full']['period1', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

            # construct model
            pyhub.construct_model()
            pyhub.construct_balances()

            counter = 0

            # Loop over each chemical pathway to unfix
            for pathways in unfix_order_pathways:
                for chemical, pathway in pathways.items():
                    if isinstance(pathway, list):  # If the pathway is a list of multiple pathways
                        for sub_pathway in pathway:
                            tech_list = pathways_ethylene[sub_pathway] if chemical == "ethylene" else pathways_ammonia[
                                sub_pathway]
                            for tech in tech_list:
                                tech_status[tech] = False
                    else:  # Single pathway case
                        tech_list = pathways_ethylene[pathway] if chemical == "ethylene" else pathways_ammonia[pathway]
                        for tech in tech_list:
                            tech_status[tech] = False

                counter += 1
                pyhub.data.model_config['reporting']['case_name']['value'] = 'ws_' + str(counter)

                fix_technology_sizes_zero(pyhub, tech_status, 'Chemelot', '2030')

                pyhub.solve()


