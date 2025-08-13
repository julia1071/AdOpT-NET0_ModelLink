import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.model_construction.extra_constraints import set_annual_export_demand, set_negative_CO2_limit
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing, \
    installed_capacities_existing_from_file

#Run Zeeland standalone scope 1-2
execute = 1

if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/Model_Linking/Full/ML_Zeeland_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/Scope1-2"

    # select simulation types
    scope3 = 0
    annual_demand = 1
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
    nr_DD_days = 10
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
            if nr_DD_days > 0:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model[
                    'clustered'].var_emissions_net.value
            else:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24 * 30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 12
        model_config['solveroptions']['nodefilestart']['value'] = 1e10

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if i != 0:
            prev_interval = intervals[i - 1]
            installed_capacities_existing(pyhub, interval, prev_interval, 'Zeeland', casepath_interval)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # change emission factor to correct for scope 3
        if not scope3:
            if nr_DD_days != 0:
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'CO2', 'Export emission factor'] = 0
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'methane', 'Import emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'CO2', 'Export emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'naphtha', 'Import emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'methane', 'Import emission factor'] = 0

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()

        # add annual constraint
        if annual_demand:
            set_annual_export_demand(pyhub[interval], interval,
                                     {'ethylene': 647310, 'PE_olefin': 1070000, 'ammonia': 1184000})

        # add DAC CO2 export limit constraint
        set_negative_CO2_limit(pyhub[interval], interval,
                               ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

        pyhub[interval].solve()

#Run Zeeland standalone scope 1-3
execute = 1

if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/Model_Linking/Full/ML_Zeeland_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/Scope1-3"

    # select simulation types
    scope3 = 1
    annual_demand = 1
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
    nr_DD_days = 10
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
            if nr_DD_days > 0:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model[
                    'clustered'].var_emissions_net.value
            else:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24 * 30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 12
        model_config['solveroptions']['nodefilestart']['value'] = 1e10

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if i != 0:
            prev_interval = intervals[i - 1]
            installed_capacities_existing(pyhub, interval, prev_interval, 'Zeeland', casepath_interval)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()

        # add annual constraint
        if annual_demand:
            set_annual_export_demand(pyhub[interval], interval,
                                     {'ethylene': 647310, 'PE_olefin': 1070000, 'ammonia': 1184000})

        # add DAC CO2 export limit constraint
        set_negative_CO2_limit(pyhub[interval], interval,
                               ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

        pyhub[interval].solve()


#Run Zeeland standalone scope 1-2, low ambition
execute = 1

if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/Model_Linking/Full/ML_Zeeland_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/LowAmbition"

    # select simulation types
    scope3 = 0
    annual_demand = 1
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 1, '2050': 1}
    nr_DD_days = 10
    pyhub = {}

    for i, interval in enumerate(intervals):
        casepath_interval = casepath + interval
        json_filepath = Path(casepath_interval) / "ConfigModel.json"

        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days

        #only costs minimization
        model_config['optimization']['objective']['value'] = 'costs'

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24 * 30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 12
        model_config['solveroptions']['nodefilestart']['value'] = 1e10

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if i != 0:
            prev_interval = intervals[i - 1]
            installed_capacities_existing(pyhub, interval, prev_interval, 'Zeeland', casepath_interval)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # change emission factor to correct for scope 3
        if not scope3:
            if nr_DD_days != 0:
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'CO2', 'Export emission factor'] = 0
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'naphtha', 'Import emission factor'] = 0
                pyhub[interval].data.time_series['clustered'][
                    interval, 'Zeeland' , 'CarrierData', 'methane', 'Import emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'CO2', 'Export emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'naphtha', 'Import emission factor'] = 0
            pyhub[interval].data.time_series['full'][
                interval, 'Zeeland' , 'CarrierData', 'methane', 'Import emission factor'] = 0

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()

        # add annual constraint
        if annual_demand:
            set_annual_export_demand(pyhub[interval], interval,
                                     {'ethylene': 647310, 'PE_olefin': 1070000, 'ammonia': 1184000})

        # add DAC CO2 export limit constraint
        set_negative_CO2_limit(pyhub[interval], interval,
                               ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

        pyhub[interval].solve()



#Run Zeeland standalone with storage
execute = 1

if execute == 1:
    # Specify the base path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/Model_Linking/Storage/ML_Zeeland_storage_bf_"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/Storage"

    # select simulation types
    scope3 = 1
    annual_demand = 0
    intervals = ['2030', '2040', '2050']
    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
    nr_DD_days = 10
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
            if nr_DD_days > 0:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model[
                    'clustered'].var_emissions_net.value
            else:
                limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # Scope 3 analysis yes/no
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24 * 30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        model_config['solveroptions']['threads']['value'] = 12
        model_config['solveroptions']['nodefilestart']['value'] = 1e10

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if i != 0:
            prev_interval = intervals[i - 1]
            installed_capacities_existing(pyhub, interval, prev_interval, 'Zeeland', casepath_interval)

        # Construct and solve the model
        pyhub[interval] = ModelHub()
        pyhub[interval].read_data(casepath_interval)

        # Set case name
        if nr_DD_days > 0:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' + str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
        else:
            pyhub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        # Start brownfield optimization
        pyhub[interval].construct_model()
        pyhub[interval].construct_balances()

        # add DAC CO2 export limit constraint
        set_negative_CO2_limit(pyhub[interval], interval,
                               ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

        pyhub[interval].solve()
