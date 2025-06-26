import json
import sys
import os
from pathlib import Path
from adopt_net0.model_construction.extra_constraints import set_annual_export_demand, set_negative_CO2_limit
from adopt_net0.modelhub import ModelHub
from adopt_net0.utilities import installed_capacities_existing


def run_zeeland(casepath, iteration_path, location, linking_energy_prices, linking_example, fast_run, intervals):
    """
    Runs the optimization loop for the cluster model for a given location and multiple intervals,
    configuring the model, linking energy prices from IESA, and setting up emission constraints.

    Args:
        casepath (str): Base path to the PyPSA cluster model case files
        iteration_path (str or Path): Path where outputs of this run will be saved
        location (str): Location to model
        linking_energy_prices (bool): Whether to link and input energy prices from IESA
        linking_example (bool): Flag for alternative linking method (not yet implemented)
        fast_run (bool): Whether to use a reduced optimization period
        intervals

    Returns:
        dict: Nested dictionary containing the input prices used for each interval and carrier,
              structured as input_cluster[location][interval][carrier] = price
    """
    print("Start the optimization in the cluster model")

    if linking_energy_prices:

        os.makedirs(iteration_path, exist_ok=True)

        # select simulation types
        scope3 = 1  # Do you want the scope 3 emissions to be accounted in the optimization?
        annual_demand = 1

        # Partly stiff and flexible P/E ratio, base on maximum demand propylene in IESA-Opt.
        carrier_demand_dict = {'ethylene': 524400, 'propylene': 235600, 'PE_olefin': 957310, 'ammonia': 1184000}
        interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}
        if fast_run:
            nr_DD_days = 0
        else:
            nr_DD_days = 10  # Set to 10 if used for full-scale modelling
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
                    limit = (interval_emissionLim[interval] *
                             pyhub[prev_interval].model['clustered'].var_emissions_net.value)
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
            if fast_run:
                # Solve model for the first 10 hours, add factor to extract_technology_outputs values of 8760/period.
                pyhub[interval].read_data(casepath_interval, start_period=0, end_period=10)
            else:
                pyhub[interval].read_data(casepath_interval)

            # Set case name
            if nr_DD_days > 0:
                pyhub[interval].data.model_config['reporting']['case_name'][
                    'value'] = (interval + '_minC_' +
                                'DD' +
                                str(pyhub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
            else:
                pyhub[interval].data.model_config['reporting']['case_name'][
                    'value'] = interval + '_minC_fullres'

            # === Input of IESA-Opt values into the cluster model ===
            #
            # # --- Naphtha ---
            # naphtha_price = (
            #         conversion_factor_IESA_to_cluster('EnergyCosts', 'Naphtha', ppi_file_path, baseyear_cluster,
            #                                           baseyear_IESA)
            #         * get_value_IESA_multiple(results_year_sheet, interval, 'EnergyCosts', Activity='Naphtha')
            # )
            # print(f"The value that is inputted for naphtha is {naphtha_price}")
            # input_cluster[location][interval]['Naphtha'] = naphtha_price
            # pyhub[interval].data.time_series['full'][
            #     interval, location, 'naphtha', 'global', 'Import price'
            # ] = naphtha_price
            #
            # # --- Bio Naphtha ---
            # bio_naphtha_price = (
            #         conversion_factor_IESA_to_cluster('EnergyCosts', 'Bio Naphtha', ppi_file_path, baseyear_cluster,
            #                                           baseyear_IESA)
            #         * get_value_IESA_multiple(results_year_sheet, interval, 'EnergyCosts', Activity='Bio Naphtha')
            # )
            # print(f"The value that is inputted for bio naphtha is {bio_naphtha_price}")
            # input_cluster[location][interval]['Bio Naphtha'] = bio_naphtha_price
            # pyhub[interval].data.time_series['full'][
            #     interval, location, 'naphtha_bio', 'global', 'Import price'
            # ] = bio_naphtha_price
            #
            # # --- Methane (Natural Gas HD) ---
            # methane_price = (
            #         conversion_factor_IESA_to_cluster('EnergyCosts', 'Natural Gas HD', ppi_file_path, baseyear_cluster,
            #                                           baseyear_IESA)
            #         * get_value_IESA_multiple(results_year_sheet, interval, 'EnergyCosts', Activity='Natural Gas HD')
            # )
            # print(f"The value that is inputted for methane is {methane_price}")
            # input_cluster[location][interval]['Natural Gas HD'] = methane_price
            # pyhub[interval].data.time_series['full'][
            #     interval, location, 'methane', 'global', 'Import price'
            # ] = methane_price
            #
            # # --- Bio Methane (only if a valid average cost is available) ---
            # avg_bio_methane_cost = calculate_avg_bio_methane_cost(filepath, interval)
            #
            # if avg_bio_methane_cost is not None:
            #     conversion_factor = conversion_factor_IESA_to_cluster(
            #         'EnergyCosts', 'methane_bio', ppi_file_path, baseyear_cluster, baseyear_IESA
            #     )
            #
            #     bio_methane_price = conversion_factor * avg_bio_methane_cost
            #
            #     print(f"The value that is inputted for bio methane is {bio_methane_price}")
            #     input_cluster[location][interval]['methane_bio'] = bio_methane_price
            #     pyhub[interval].data.time_series['full'][
            #         interval, location, 'methane_bio', 'global', 'Import price'
            #     ] = bio_methane_price
            # else:
            #     print(f"No average bio methane cost available for interval {interval}, skipping input.")

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

    elif linking_example:
        print("Not yet defined, model linking stops")
        return sys.exit()


casepath = "U:/Data AdOpt-NET0/Test/Case_Study/ML_Zeeland_bf_"
iteration_path = "U:/Data AdOpt-NET0/Test/Result path"
location = "Zeeland"
linking_energy_prices = True
linking_example = False
fast_run = True
intervals = ['2030', '2040', '2050']

run_zeeland(casepath, iteration_path, location, linking_energy_prices, linking_example, fast_run, intervals)