import json
import sys
import os
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.model_construction.extra_constraints import set_annual_export_demand, set_negative_CO2_limit
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary
from adopt_net0.utilities import fix_installed_capacities, installed_capacities_existing
from extract_data_IESA import get_value_IESA
from conversion_factors import conversion_factor_IESA_to_cluster

def run_Zeeland(casepath, iteration_path, i, location, linking_energy_prices, linking_mpw, results_year_sheet, ppi_file_path, baseyear_cluster, baseyear_IESA):
    print("Start the optimization in the cluster model")

    if linking_energy_prices:

        os.makedirs(iteration_path, exist_ok=True)

        # select simulation types
        scope3 = 1 # Do you want the scope 3 emissions to be accounted in the optimization?
        annual_demand = 1
        carrier_demand_dict = {'ethylene': 1184352, 'propylene': 532958, 'ammonia': 1184000}
        intervals = ['2030', '2040', '2050']
        interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
        nr_DD_days = 0 # Set to 10 if used for full-scale modelling also change the 876 factor in the extract_technology_output
        pyhub = {}

        input_cluster = {}
        if location not in input_cluster:
            input_cluster[location] = {}


        for i, interval in enumerate(intervals):
            casepath_interval = casepath + interval
            json_filepath = Path(casepath_interval) / "ConfigModel.json"
            if interval not in input_cluster[location]:
                input_cluster[location][interval] = {}
            with open(json_filepath) as json_file:
                model_config = json.load(json_file)

            model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days

            if interval == '2030':
                model_config['optimization']['objective']['value'] = 'costs'
            else:
                prev_interval = intervals[i - 1]
                model_config['optimization']['objective']['value'] = "costs_emissionlimit"
                if nr_DD_days > 0:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model['clustered'].var_emissions_net.value
                else:
                    limit = interval_emissionLim[interval] * pyhub[prev_interval].model['full'].var_emissions_net.value
                model_config['optimization']['emission_limit']['value'] = limit

            # other constraint options
            model_config['optimization']['scope_three_analysis']['value'] = scope3

            # solver settings
            model_config['solveroptions']['timelim']['value'] = 24*30
            model_config['solveroptions']['mipgap']['value'] = 0.01
            model_config['solveroptions']['threads']['value'] = 8
            model_config['solveroptions']['nodefilestart']['value'] = 200

            # change save options
            model_config['reporting']['save_summary_path']['value'] = str(iteration_path)
            model_config['reporting']['save_path']['value'] = str(iteration_path)

            # Write the updated JSON data back to the file
            with open(json_filepath, 'w') as json_file:
                json.dump(model_config, json_file, indent=4)

            if i != 0:
                prev_interval = intervals[i - 1]
                installed_capacities_existing(pyhub, interval, prev_interval, location, casepath_interval)

            # Construct and solve the model
            pyhub[interval] = ModelHub()
            pyhub[interval].read_data(casepath_interval, start_period=0,end_period=10) # Solve model for the first 10 hours, NN-days must be set to 10 again with full-scale modelling

            # Set case name
            if nr_DD_days > 0:
                pyhub[interval].data.model_config['reporting']['case_name'][
                    'value'] = (interval + '_minC_' +
                                'DD' + str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
            else:
                pyhub[interval].data.model_config['reporting']['case_name'][
                    'value'] = interval + '_minC_fullres'

            #Input of IESA-Opt values in cluster model

            x = (conversion_factor_IESA_to_cluster('EnergyCosts','Naphtha', ppi_file_path, baseyear_cluster,
                                                    baseyear_IESA) * get_value_IESA (results_year_sheet, interval,
                                                                        'EnergyCosts', 'Naphtha'))
            print(f"The value that is inputed for naphtha is {x}")
            input_cluster[location][interval]['Naphtha'] = x
            pyhub[interval].data.time_series['full'][
                interval, location, 'naphtha', 'global', 'Import price'] = x

            y = (conversion_factor_IESA_to_cluster('EnergyCosts','Bio Naphtha', ppi_file_path, baseyear_cluster,
                                                    baseyear_IESA) * get_value_IESA (results_year_sheet, interval,
                                                                        'EnergyCosts', 'Bio Naphtha'))
            print(f"The value that is inputed for bio naphtha is {y}")
            input_cluster[location][interval]['Bio Naphtha'] = y
            pyhub[interval].data.time_series['full'][
                interval, location, 'naphtha_bio', 'global', 'Import price'] = y


            z = (conversion_factor_IESA_to_cluster('EnergyCosts','Natural Gas HD', ppi_file_path, baseyear_cluster,
                                                    baseyear_IESA) * get_value_IESA (results_year_sheet, interval,
                                                                        'EnergyCosts', 'Natural Gas HD'))
            print(f"The value that is inputed for methane is {z}")
            input_cluster[location][interval]['Natural Gas HD'] = z
            pyhub[interval].data.time_series['full'][
                interval, location, 'methane', 'global', 'Import price'] = z


            # #pyhub[interval].data.time_series['full'][
            #     interval, location, 'biomass', 'global', 'Import price'] = (conversion_factor_IESA_to_cluster('EnergyCosts',
            #                                                                                              'Biomass',
            #                                                                                              ppi_file_path,
            #                                                                                              baseyear_cluster,
            #                                                                                              baseyear_IESA) *
            #                                                             get_value_IESA ( results_year_sheet, interval, 'EnergyCosts', 'Biomass'))
            # Start brownfield optimization
            pyhub[interval].construct_model()
            pyhub[interval].construct_balances()

            # add annual constraint
            if annual_demand:
                set_annual_export_demand(pyhub[interval], interval, carrier_demand_dict)

            # add DAC CO2 export limit constraint
            set_negative_CO2_limit(pyhub[interval], interval,
                                   ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

            pyhub[interval].solve()

        return input_cluster

    elif linking_mpw:
        print("Not yet defined, model linking stops")
        return sys.exit()

