import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing

#Run Chemelot cluster case
execute = 1


if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Brownfield/"


    # select simulation types
    node = 'Chemelot'
    objectives = ['costs']
    co2tax = ['ref']
    scope3 = 1
    scenarios = ['2030', '2040', '2050']
    scenario_taxHigh = {'2030': 250, '2040': 400, '2050': 500}
    nr_DD_days = 0
    pyhub = {}

    for obj in objectives:
        for tax in co2tax:
            for i, scenario in enumerate(scenarios):
                casepath_period = casepath + scenario
                json_filepath = Path(casepath_period) / "ConfigModel.json"

                with open(json_filepath) as json_file:
                    model_config = json.load(json_file)

                model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days
                model_config['optimization']['objective']['value'] = obj

                # Scope 3 analysis yes/no
                model_config['optimization']['scope_three_analysis'] = scope3

                # solver settings
                model_config['solveroptions']['timelim']['value'] = 48
                model_config['solveroptions']['mipgap']['value'] = 0.01
                model_config['solveroptions']['threads']['value'] = 10

                #change save options
                model_config['reporting']['save_summary_path']['value'] = resultpath + node
                model_config['reporting']['save_path']['value'] = resultpath + node
                # Write the updated JSON data back to the file
                with open(json_filepath, 'w') as json_file:
                    json.dump(model_config, json_file, indent=4)

                if i != 0:
                    prev_scenario = scenarios[i - 1]
                    installed_capacities_existing(pyhub, scenario, prev_scenario, node, casepath_period)

                # Construct and solve the model
                pyhub[scenario] = ModelHub()
                pyhub[scenario].read_data(casepath_period)

                if obj == 'emissions_minC':
                    # add casename
                    pyhub[scenario].data.model_config['reporting']['case_name']['value'] = scenario + '_minE_refCO2tax'

                elif obj == 'costs':
                    # add casename
                    pyhub[scenario].data.model_config['reporting']['case_name']['value'] = scenario + '_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub[scenario].data.time_series['clustered'][
                                scenario, node, 'CarbonCost', 'global', 'price'] = scenario_taxHigh[scenario]
                        pyhub[scenario].data.time_series['full'][scenario, node, 'CarbonCost', 'global', 'price'] = scenario_taxHigh[scenario]

                # Start brownfield optimization
                pyhub[scenario].construct_model()
                pyhub[scenario].construct_balances()
                pyhub[scenario].solve()



#Run Chemelot cluster case with minimum size constraint
execute = 0
nr_DD_days = 0

if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Brownfield/"


    # select simulation types
    node = 'Chemelot'
    objectives = ['costs']
    co2tax = ['ref']
    scope3 = 1
    scenarios = ['2030', '2040', '2050']
    pyhub = {}
    set_conv_tech = ["SteamReformer_existing", "HaberBosch_existing", "CrackerFurnace_existing", "OlefinSeparation_existing"]

    for obj in objectives:
        for tax in co2tax:
            for i, scenario in enumerate(scenarios):
                casepath_period = casepath + scenario
                json_filepath = Path(casepath_period) / "ConfigModel.json"

                with open(json_filepath) as json_file:
                    model_config = json.load(json_file)

                model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days
                model_config['optimization']['objective']['value'] = obj

                # Scope 3 analysis yes/no
                model_config['optimization']['scope_three_analysis'] = scope3

                #change save options
                model_config['reporting']['save_summary_path']['value'] = resultpath + node
                model_config['reporting']['save_path']['value'] = resultpath + node
                # Write the updated JSON data back to the file
                with open(json_filepath, 'w') as json_file:
                    json.dump(model_config, json_file, indent=4)

                # Construct and solve the model
                pyhub[scenario] = ModelHub()
                pyhub[scenario].read_data(casepath_period, start_period=1, end_period=10)

                if obj == 'emissions_minC':
                    # add casename
                    pyhub[scenario].data.model_config['reporting']['case_name']['value'] = scenario + '_minE_refCO2tax'

                elif obj == 'costs':
                    # add casename
                    pyhub[scenario].data.model_config['reporting']['case_name']['value'] = scenario + '_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub[scenario].data.time_series['clustered'][
                                scenario, node, 'CarbonCost', 'global', 'price'] = 250
                        pyhub[scenario].data.time_series['full'][scenario, node, 'CarbonCost', 'global', 'price'] = 250

                # Start brownfield optimization
                pyhub[scenario].construct_model()
                pyhub[scenario].construct_balances()

                if i != 0:
                    prev_scenario = scenarios[i - 1]
                    pyhub = fix_installed_capacities(pyhub, scenario, prev_scenario, node, set_conv_tech)

                pyhub[scenario].solve()

                # ref = pyhub['2040'].model[pyhub[scenario].info_solving_algorithms["aggregation_model"]].periods[scenario].node_blocks[node].tech_blocks_active['SteamReformer']



