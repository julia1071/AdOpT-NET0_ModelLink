import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing, \
    installed_capacities_existing_from_file

#Run Chemelot cluster case
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_gf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/EmissionScope Greenfield/"
    json_filepath = Path(casepath) / "ConfigModel.json"

    sensitivity = 'MPWemission'
    scope3 = 1
    run_with_emission_limit = 1
    # intervals = ['2040', '2050']
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
    nr_DD_days = 10
    take_prev_solution = 0
    emission_2040 = 1587293.557
    pyhub = {}

    for i, interval in enumerate(intervals):
        casepath_interval = casepath + interval
        json_filepath = Path(casepath_interval) / "ConfigModel.json"

        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days

        if interval == '2030':
            model_config['optimization']['objective']['value'] = 'costs'
        else:
            prev_interval = intervals[i - 1]
            model_config['optimization']['objective']['value'] = "costs_emissionlimit"
            if interval == '2040' and take_prev_solution:
                limit = interval_emissionLim[interval] * emission_2040
            elif interval == '2050' and take_prev_solution:
                limit = 0
            else:
                if nr_DD_days > 0:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model[
                        'clustered'].var_emissions_net.value
                else:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24*30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 24
        model_config['solveroptions']['nodefilestart']['value'] = 400

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath + sensitivity
        model_config['reporting']['save_path']['value'] = resultpath + sensitivity

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # change emission factor to MPW gasification direct emissions
        if nr_DD_days != 0:
            pyhub[interval].data.time_series['clustered'][
                interval, 'Chemelot', 'CarrierData', 'MPW', 'Import emission factor'] = 1.349
        pyhub[interval].data.time_series['full'][
            interval, 'Chemelot', 'CarrierData', 'MPW', 'Import emission factor'] = 1.349

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(
                        pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
            pyhub[interval].data.time_series['clustered'][
                interval, 'Chemelot', 'CarbonCost', 'global', 'price'] = 150.31
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        pyhub[interval].data.time_series['full'][interval, 'Chemelot', 'CarbonCost', 'global', 'price'] = 150.31

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()
        pyhub[interval].solve()


#Run Chemelot cluster case brownfield
execute = 1


if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/EmissionScope Brownfield/"

    # select simulation types
    sensitivity = 'MPWemission'
    scope3 = 1
    run_with_emission_limit = 1
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
    nr_DD_days = 10
    prev_from_file = 0
    emission_2030 = 2125646.443
    h5_path_prev = Path(
        "Z:/AdOpt_NET0/AdOpt_results/MY/EmissionScope Brownfield/Chemelot/20250408154915_2030_minC_DD10-1/optimization_results.h5")
    pyhub = {}

    for i, interval in enumerate(intervals):
        casepath_interval = casepath + interval
        json_filepath = Path(casepath_interval) / "ConfigModel.json"

        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days

        if interval == '2030':
            model_config['optimization']['objective']['value'] = 'costs'
        else:
            prev_interval = intervals[i - 1]
            model_config['optimization']['objective']['value'] = "costs_emissionlimit"
            if interval == '2040' and prev_from_file:
                limit = interval_emissionLim[interval] * emission_2030
            else:
                if nr_DD_days > 0:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model[
                        'clustered'].var_emissions_net.value
                else:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24*30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 24
        model_config['solveroptions']['nodefilestart']['value'] = 400

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath + sensitivity
        model_config['reporting']['save_path']['value'] = resultpath + sensitivity
        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if interval != '2030':
            prev_interval = intervals[i - 1]
            if prev_from_file and interval == '2040':
                if h5_path_prev.exists():
                    installed_capacities_existing_from_file(interval, '2030', 'Chemelot', casepath_interval,
                                                            h5_path_prev)
            else:
                installed_capacities_existing(pyhub, interval, prev_interval, 'Chemelot', casepath_interval)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # change emission factor to MPW gasification direct emissions
        if nr_DD_days != 0:
            pyhub[interval].data.time_series['clustered'][
                interval, 'Chemelot', 'CarrierData', 'MPW', 'Import emission factor'] = 1.349
        pyhub[interval].data.time_series['full'][
            interval, 'Chemelot', 'CarrierData', 'MPW', 'Import emission factor'] = 1.349

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(
                        pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
            pyhub[interval].data.time_series['clustered'][
                interval, 'Chemelot', 'CarbonCost', 'global', 'price'] = 150.31
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        pyhub[interval].data.time_series['full'][interval, 'Chemelot', 'CarbonCost', 'global', 'price'] = 150.31

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()
        pyhub[interval].solve()



