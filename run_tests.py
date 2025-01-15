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
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/Tests/MY_Chemelot_test_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/tests/"


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
                # model_config['solveroptions']['threads']['value'] = 10

                #change save options
                model_config['reporting']['save_summary_path']['value'] = resultpath
                model_config['reporting']['save_path']['value'] = resultpath
                # Write the updated JSON data back to the file
                with open(json_filepath, 'w') as json_file:
                    json.dump(model_config, json_file, indent=4)

                if i != 0:
                    prev_interval = intervals[i - 1]
                    installed_capacities_existing(pyhub, interval, prev_interval, node, casepath_interval)

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
                                interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]
                        pyhub[interval].data.time_series['full'][interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]

                # Start brownfield optimization
                pyhub[interval].construct_model()
                pyhub[interval].construct_balances()
                pyhub[interval].solve()


#Run Chemelot cluster case
execute = 0


if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/Tests/MY_Chemelot_test_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/tests/"


    # select simulation types
    node = 'Chemelot'
    objectives = ['costs']
    co2tax = ['ref']
    scope3 = 1
    scenarios = ['2030', '2040', '2050']
    # scenarios = ['2030']
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

                #change save options
                model_config['reporting']['save_summary_path']['value'] = resultpath
                model_config['reporting']['save_path']['value'] = resultpath
                # Write the updated JSON data back to the file
                with open(json_filepath, 'w') as json_file:
                    json.dump(model_config, json_file, indent=4)

                if i != 0:
                    prev_scenario = scenarios[i - 1]
                    installed_capacities_existing(pyhub, scenario, prev_scenario, node, casepath_period)

                #change carrier data
                dp.fill_carrier_data(casepath_period, value_or_data=1734, columns=['Import price'], carriers=['ethanol'])
                dp.fill_carrier_data(casepath_period, value_or_data=1473, columns=['Import price'], carriers=['propane'])

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
                                scenario, node, 'CarbonCost', 'global', 'price'] = scenario_taxHigh[scenario]
                        pyhub[scenario].data.time_series['full'][scenario, node, 'CarbonCost', 'global', 'price'] = scenario_taxHigh[scenario]

                # Start brownfield optimization
                pyhub[scenario].construct_model()
                pyhub[scenario].construct_balances()
                pyhub[scenario].solve()



