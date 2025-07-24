import json
import os
from pathlib import Path

import config_model_linking as cfg

from adopt_net0.model_construction.extra_constraints import set_annual_export_demand, set_negative_CO2_limit
from adopt_net0.modelhub import ModelHub
from adopt_net0.utilities import installed_capacities_existing


def run_adopt(case_path, iteration_path, cluster_input_dict):
    """
    Runs the optimization loop for the cluster model for a given location and multiple intervals,
    configuring the model, linking energy prices from IESA, and setting up emission constraints.

    Args:
        case_path (str): Base path to the PyPSA cluster model case files
        iteration_path (str or Path): Path where outputs of this run will be saved
        cluster_input_dict (dict): dictionary with input links for cluster model
    Returns:
        dict: Nested dictionary containing the input prices used for each interval and carrier,
              structured as input_cluster[location][interval][carrier] = price
    """
    print("Start the optimization in the cluster model")

    os.makedirs(iteration_path, exist_ok=True)

    # select simulation types
    scope3 = cfg.scope3  # Do you want the scope 3 emissions to be accounted in the optimization?
    annual_demand = 1

    interval_emissionLim = {'2030': 1, '2040': 0.5, '2050': 0}

    if cfg.fast_run:
        nr_DD_days = 0
    else:
        nr_DD_days = 10  # Set to 10 if used for full-scale modelling
    adopt_hub = {}


    for i, interval in enumerate(cfg.intervals):
        casepath_interval = case_path + interval
        json_filepath = Path(casepath_interval) / "ConfigModel.json"

        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days

        if interval == '2030':
            model_config['optimization']['objective']['value'] = 'costs'
        else:
            prev_interval = cfg.intervals[i - 1]
            model_config['optimization']['objective']['value'] = "costs_emissionlimit"
            if nr_DD_days > 0:
                limit = (interval_emissionLim[interval] *
                         adopt_hub[prev_interval].model['clustered'].var_emissions_net.value)
            else:
                limit = interval_emissionLim[interval] * adopt_hub[prev_interval].model['full'].var_emissions_net.value
            model_config['optimization']['emission_limit']['value'] = limit

        # other constraint options
        model_config['optimization']['scope_three_analysis']['value'] = scope3

        # solver settings
        model_config['solveroptions']['timelim']['value'] = 24*30
        model_config['solveroptions']['mipgap']['value'] = 0.01
        if cfg.threads:
            model_config['solveroptions']['threads']['value'] = cfg.threads
        # model_config['solveroptions']['nodefilestart']['value'] = 200

        # change save options
        model_config['reporting']['save_summary_path']['value'] = str(iteration_path)
        model_config['reporting']['save_path']['value'] = str(iteration_path)

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        if i != 0:
            prev_interval = cfg.intervals[i - 1]
            installed_capacities_existing(adopt_hub, interval, prev_interval, cfg.location, casepath_interval)

        # Construct and solve the model
        adopt_hub[interval] = ModelHub()
        if cfg.fast_run:
            # Solve model for the first 10 hours
            adopt_hub[interval].read_data(casepath_interval, start_period=0, end_period=10)
        else:
            adopt_hub[interval].read_data(casepath_interval)

        # Set case name
        if nr_DD_days > 0:
            adopt_hub[interval].data.model_config['reporting']['case_name'][
                'value'] = (interval + '_minC_' +
                            'DD' +
                            str(adopt_hub[interval].data.model_config['optimization']['typicaldays']['N']['value']))
        else:
            adopt_hub[interval].data.model_config['reporting']['case_name'][
                'value'] = interval + '_minC_fullres'

        if cfg.linking_energy_prices:
            # === Input of IESA-Opt values into the cluster model ===
            for key in cluster_input_dict[cfg.location][interval].keys():
                if key in adopt_hub[interval].data.time_series['full'][interval, cfg.location, 'CarrierData']:
                    value = cluster_input_dict[cfg.location][interval][key]

                    if value is not None:
                        #Read value in adopt
                        adopt_hub[interval].data.time_series['full'][
                            interval, cfg.location, 'CarrierData', key, 'Import price'
                        ] = value
                        if nr_DD_days > 0:
                            adopt_hub[interval].data.time_series['clustered'][
                                interval, cfg.location, 'CarrierData', key, 'Import price'
                            ] = value

                        print(f"The input price for {key} is {value}")

                    else:
                        # check if carrier has international import
                        if key in cfg.car_import_international:
                            print(f"The input price for {key} is not updated as there is no national supply.")
                        else:
                            # Read value in adopt
                            adopt_hub[interval].data.time_series['full'][
                                interval, cfg.location, 'CarrierData', key, 'Import limit'
                            ] = 0
                            if nr_DD_days > 0:
                                adopt_hub[interval].data.time_series['clustered'][
                                    interval, cfg.location, 'CarrierData', key, 'Import limit'
                                ] = 0

                            print(f"The import limit for {key} is 0")

        if cfg.linking_MPW:
            total_mpw_supply = cluster_input_dict[cfg.location][interval]['Import limit MPW']

            adopt_hub[interval].data.time_series['full'][
                interval, cfg.location, 'CarrierData', 'MPW', 'Import limit'
            ] = total_mpw_supply
            if nr_DD_days > 0:
                adopt_hub[interval].data.time_series['clustered'][
                    interval, cfg.location, 'CarrierData', 'MPW', 'Import limit'
                ] = total_mpw_supply

            print(f"The import limit for MPW is {total_mpw_supply:.2f}")

        # Start brownfield optimization
        adopt_hub[interval].construct_model()
        adopt_hub[interval].construct_balances()

        # add annual constraint
        if annual_demand:
            set_annual_export_demand(adopt_hub[interval], interval, cfg.carrier_demand_dict)

        # add DAC CO2 export limit constraint
        set_negative_CO2_limit(adopt_hub[interval], interval,
                               ["SteamReformer", "WGS_m", "SteamReformer_existing", "WGS_m_existing"])

        adopt_hub[interval].solve()

    return adopt_hub



