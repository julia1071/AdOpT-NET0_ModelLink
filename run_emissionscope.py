import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing


#Run Chemelot cluster case
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_gf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/EmissionScope/"
    json_filepath = Path(casepath) / "ConfigModel.json"

    node = 'Chemelot'
    objectives = ['costs']
    scope3 = 0
    run_with_emission_limit = 1
    intervals = ['2030', '2040', '2050']
    co2tax = ['ref']
    interval_taxHigh = {'2030': 250, '2040': 400, '2050': 500}
    nr_DD_days = 0

    for obj in objectives:
        for tax in co2tax:
            for i, interval in enumerate(intervals):
                casepath_period = casepath + interval
                json_filepath = Path(casepath_period) / "ConfigModel.json"

                with open(json_filepath) as json_file:
                    model_config = json.load(json_file)

                model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days
                model_config['optimization']['objective']['value'] = obj

                # Scope 3 analysis yes/no
                model_config['optimization']['scope_three_analysis'] = scope3

                # solver settings
                model_config['solveroptions']['timelim']['value'] = 168
                model_config['solveroptions']['mipgap']['value'] = 0.01
                model_config['solveroptions']['threads']['value'] = 10

                #change save options
                model_config['reporting']['save_summary_path']['value'] = resultpath + node
                model_config['reporting']['save_path']['value'] = resultpath + node

                # Write the updated JSON data back to the file
                with open(json_filepath, 'w') as json_file:
                    json.dump(model_config, json_file, indent=4)

                # Construct and solve the model
                pyhub = ModelHub()
                pyhub.read_data(casepath_period)

                # change emission factor to correct for scope 3
                if not scope3:
                    if nr_DD_days != 0:
                        pyhub.data.time_series['clustered'][
                            interval, node, 'CarrierData', 'CO2', 'Export emission factor'] = 0
                        pyhub.data.time_series['clustered'][
                            interval, node, 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                        pyhub.data.time_series['clustered'][
                            interval, node, 'CarrierData', 'methane', 'Import emission factor'] = 0
                    pyhub.data.time_series['full'][
                        interval, node, 'CarrierData', 'CO2', 'Export emission factor'] = 0
                    pyhub.data.time_series['full'][
                        interval, node, 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                    pyhub.data.time_series['full'][
                        interval, node, 'CarrierData', 'methane', 'Import emission factor'] = 0

                if obj == 'emissions_minC':
                    # add casename
                    pyhub.data.model_config['reporting']['case_name']['value'] = interval + '_gf_minE_refCO2tax'

                    # solving
                    pyhub.quick_solve()

                elif obj == 'costs':
                    # add casename
                    pyhub.data.model_config['reporting']['case_name'][
                        'value'] = interval + '_gf_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub.data.time_series['clustered'][
                                interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]
                        pyhub.data.time_series['full'][
                            interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]

                    # solving
                    pyhub.quick_solve()

                    if interval == '2050' and run_with_emission_limit:
                        casepath_interval = casepath + interval
                        json_filepath = Path(casepath_interval) / "ConfigModel.json"

                        with open(json_filepath) as json_file:
                            model_config = json.load(json_file)

                        model_config['optimization']['objective']['value'] = "costs_emissionlimit"
                        model_config['optimization']['emission_limit']['value'] = 0

                        # Write the updated JSON data back to the file
                        with open(json_filepath, 'w') as json_file:
                            json.dump(model_config, json_file, indent=4)

                        # Construct and solve the model
                        pyhub = ModelHub()
                        pyhub.read_data(casepath_interval)

                        # add casename
                        if nr_DD_days > 0:
                            pyhub.data.model_config['reporting']['case_name'][
                                'value'] = ('2050_emissionlimit_minC_' + tax + 'CO2tax' +
                                            'DD' + str(
                                        pyhub["2050_emissionlimit"].data.model_config['optimization']['typicaldays'][
                                            'N']['value']))
                        else:
                            pyhub.data.model_config['reporting']['case_name'][
                                'value'] = ('2050_emissionlimit_minC_' + tax + 'CO2tax_fullres')

                        # Start brownfield optimization
                        pyhub.quick_solve()


#Run Chemelot cluster case
execute = 1


if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/EmissionScope/"


    # select simulation types
    node = 'Chemelot'
    objectives = ['costs']
    co2tax = ['ref']
    scope3 = 0
    run_with_emission_limit = 1
    intervals = ['2030', '2040', '2050']
    interval_taxHigh = {'2030': 250, '2040': 400, '2050': 500}
    nr_DD_days = 0
    pyhub = {}

    for obj in objectives:
        for tax in co2tax:
            for i, interval in enumerate(intervals):
                casepath_period = casepath + interval
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
                    prev_interval = intervals[i - 1]
                    installed_capacities_existing(pyhub, interval, prev_interval, node, casepath_period)

                # Construct and solve the model
                pyhub[interval] = ModelHub()
                pyhub[interval].read_data(casepath_period)

                #change emission factor to correct for scope 3
                if not scope3:
                    if nr_DD_days != 0:
                        pyhub[interval].data.time_series['clustered'][
                            interval, node, 'CarrierData', 'CO2', 'Export emission factor'] = 0
                        pyhub[interval].data.time_series['clustered'][
                            interval, node, 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                        pyhub[interval].data.time_series['clustered'][
                            interval, node, 'CarrierData', 'methane', 'Import emission factor'] = 0
                    pyhub[interval].data.time_series['full'][
                        interval, node, 'CarrierData', 'CO2', 'Export emission factor'] = 0
                    pyhub[interval].data.time_series['full'][
                        interval, node, 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                    pyhub[interval].data.time_series['full'][
                        interval, node, 'CarrierData', 'methane', 'Import emission factor'] = 0

                if obj == 'emissions_minC':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_bf_minE_refCO2tax'

                elif obj == 'costs':
                    # add casename
                    pyhub[interval].data.model_config['reporting']['case_name']['value'] = interval + '_bf_minC_' + tax + 'CO2tax'

                    if tax == 'high':
                        if nr_DD_days != 0:
                            pyhub[interval].data.time_series['clustered'][
                                interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]
                        pyhub[interval].data.time_series['full'][interval, node, 'CarbonCost', 'global', 'price'] = interval_taxHigh[interval]

                # Start brownfield optimization
                pyhub[interval].construct_model()
                pyhub[interval].construct_balances()
                pyhub[interval].solve()

                if interval == '2050' and run_with_emission_limit:
                    casepath_interval = casepath + interval
                    json_filepath = Path(casepath_interval) / "ConfigModel.json"

                    with open(json_filepath) as json_file:
                        model_config = json.load(json_file)

                    model_config['optimization']['objective']['value'] = "costs_emissionlimit"
                    model_config['optimization']['emission_limit']['value'] = 0

                    # Write the updated JSON data back to the file
                    with open(json_filepath, 'w') as json_file:
                        json.dump(model_config, json_file, indent=4)

                    # fix to 2040 capacities
                    prev_interval = intervals[i - 1]
                    installed_capacities_existing(pyhub, interval, prev_interval, node, casepath_interval)

                    # Construct and solve the model
                    pyhub["2050_emissionlimit"] = ModelHub()
                    pyhub["2050_emissionlimit"].read_data(casepath_interval)

                    # add casename
                    if nr_DD_days > 0:
                        pyhub["2050_emissionlimit"].data.model_config['reporting']['case_name'][
                            'value'] = ('2050_emissionlimit_minC_' + tax + 'CO2tax' +
                                        'DD' + str(pyhub["2050_emissionlimit"].data.model_config['optimization']['typicaldays']['N']['value']))
                    else:
                        pyhub["2050_emissionlimit"].data.model_config['reporting']['case_name'][
                            'value'] = ('2050_emissionlimit_minC_' + tax + 'CO2tax_fullres')

                    # Start brownfield optimization
                    pyhub["2050_emissionlimit"].construct_model()
                    pyhub["2050_emissionlimit"].construct_balances()
                    pyhub["2050_emissionlimit"].solve()



