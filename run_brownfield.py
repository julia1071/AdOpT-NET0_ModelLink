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
    intervals = ['2030', '2040', '2050']
    interval_taxHigh = {'2030': 250, '2040': 400, '2050': 500}
    nr_DD_days = 0
    pyhub = {}

    for obj in objectives:
        for tax in co2tax:
            for i, interval in enumerate(intervals):
                casepath_interval = casepath + interval
                json_filepath = Path(casepath_interval) / "ConfigModel.json"

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
                    prev_interval = intervals[i - 1]
                    installed_capacities_existing(pyhub, interval, prev_interval, node, casepath_interval)

                # Construct and solve the model
                pyhub[interval] = ModelHub()
                pyhub[interval].read_data(casepath_interval)

                if obj == 'emissions_minC':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_minE_refCO2tax'

                elif obj == 'costs':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub[interval].data.time_series['clustered'][
                                interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]
                        pyhub[interval].data.time_series['full'][interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]

                # Start brownfield optimization
                pyhub[interval].construct_model()
                pyhub[interval].construct_balances()
                pyhub[interval].solve()



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
    intervals = ['2030', '2040', '2050']
    pyhub = {}
    set_conv_tech = ["SteamReformer_existing", "HaberBosch_existing", "CrackerFurnace_existing", "OlefinSeparation_existing"]

    for obj in objectives:
        for tax in co2tax:
            for i, interval in enumerate(intervals):
                casepath_interval = casepath + interval
                json_filepath = Path(casepath_interval) / "ConfigModel.json"

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
                pyhub[interval] = ModelHub()
                pyhub[interval].read_data(casepath_interval, start_period=1, end_period=10)

                if obj == 'emissions_minC':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_minE_refCO2tax'

                elif obj == 'costs':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub[interval].data.time_series['clustered'][
                                interval, node, 'CarbonCost', 'global', 'price'] = 250
                        pyhub[interval].data.time_series['full'][interval, node, 'CarbonCost', 'global', 'price'] = 250

                # Start brownfield optimization
                pyhub[interval].construct_model()
                pyhub[interval].construct_balances()

                if i != 0:
                    prev_interval = intervals[i - 1]
                    pyhub = fix_installed_capacities(pyhub, interval, prev_interval, node, set_conv_tech)

                pyhub[interval].solve()

                # ref = pyhub['2040'].model[pyhub[interval].info_solving_algorithms["aggregation_model"]].intervals[interval].node_blocks[node].tech_blocks_active['SteamReformer']



