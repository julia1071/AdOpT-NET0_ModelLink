import json
from pathlib import Path
import pandas as pd
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary


#Run Chemelot test design days
execute = 1
linear = 0

if execute == 1:
    if linear:
        # Specify the path to your input data
        casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030_linear"
        resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/DesignDays/CH_2030_linear"
    else:
        # Specify the path to your input data
        casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030"
        resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/DesignDays/CH_2030"

    json_filepath = Path(casepath) / "ConfigModel.json"

    co2tax = ['ref', 'high']
    DD = [10, 20, 40, 60, 100, 200, 0]
    # DD = [0]

    for tax in co2tax:
        for nr in DD:
            with open(json_filepath) as json_file:
                model_config = json.load(json_file)

            # change save options
            model_config['reporting']['save_summary_path']['value'] = resultpath + '_' + tax + 'CO2tax'
            model_config['reporting']['save_path']['value'] = resultpath + '_' + tax + 'CO2tax'

            model_config['optimization']['typicaldays']['N']['value'] = nr
            model_config['optimization']['objective']['value'] = 'costs'

            # Write the updated JSON data back to the file
            with open(json_filepath, 'w') as json_file:
                json.dump(model_config, json_file, indent=4)

            # Construct and solve the model
            pyhub = ModelHub()
            pyhub.read_data(casepath)

            if tax == 'high':
                if nr != 0:
                    pyhub.data.time_series['clustered']['2030', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                pyhub.data.time_series['full']['2030', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

            #add casename based on resolution
            if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
                pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
            else:
                pyhub.data.model_config['reporting']['case_name']['value'] = 'DD' + str(pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

            #solving
            pyhub.quick_solve()



#Run Chemelot cluster case
execute = 0
nr_DD_days = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/AdOpt_NET0/AdOpt_casestudies/MY/MY_Chemelot_2030"
    resultpath = "Z:/AdOpt_NET0/AdOpt_results/MY/Baseline/CH_2030"
    json_filepath = Path(casepath) / "ConfigModel.json"

    # objectives = ['costs', 'emissions_minC']
    objectives = ['costs']

    for obj in objectives:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr_DD_days
        model_config['optimization']['objective']['value'] = obj

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath


        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        if obj == 'emissions_minC':
            # add casename
            pyhub.data.model_config['reporting']['case_name']['value'] = 'minE_refCO2tax'

            # solving
            pyhub.quick_solve()

        elif obj == 'costs':
            co2tax = ['ref', 'high']

            for tax in co2tax:
                # add casename
                pyhub.data.model_config['reporting']['case_name']['value'] = 'minC_' + tax + 'CO2tax'

                if tax == 'high':
                    if nr_DD_days != 0:
                        pyhub.data.time_series['clustered'][
                            '2030', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250
                    pyhub.data.time_series['full']['2030', 'Chemelot', 'CarbonCost', 'global', 'price'] = 250

                # solving
                pyhub.quick_solve()
