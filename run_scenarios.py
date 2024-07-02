import json
from pathlib import Path
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary


#Run Chemelot case study min costs
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    resultpath = "Z:/PyHub/PyHub_results/CM/Chemelot_cluster"
    json_filepath = Path(casepath) / "ConfigModel.json"

    TD = [10, 20, 40, 60, 100, 200, 0]

    for nr in TD:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr
        model_config['optimization']['objective']['value'] = 'costs'
        model_config['optimization']['emission_limit']['value'] = 0

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath


        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        # pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

        #add casename based on resolution
        if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
            pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
        else:
            pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

        #solving
        pyhub.quick_solve()

# Run Chemelot case study emissions
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    resultpath = "Z:/PyHub/PyHub_results/CM/Chemelot_cluster_minE"
    json_filepath = Path(casepath) / "ConfigModel.json"

    # TD = [10, 20, 40, 60, 100, 200, 0]
    TD = [10, 20, 40, 60, 100, 200, 0]


    for nr in TD:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = nr
        model_config['optimization']['objective']['value'] = 'emissions_minC'
        model_config['optimization']['emission_limit']['value'] = 0

        # change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

        # add casename based on resolution
        if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
            pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
        else:
            pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(
                pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

        # solving
        pyhub.quick_solve()



#Run Chemelot case study relaxed
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster_relaxed"
    resultpath = "Z:/PyHub/PyHub_results/CM/RDS3_Chemelot_cluster_relaxed"
    json_filepath = Path(casepath) / "ConfigModel.json"

    obj = ['costs', 'emissions_minC']

    for nr in obj:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        model_config['optimization']['typicaldays']['N']['value'] = 0
        model_config['optimization']['objective']['value'] = nr
        model_config['optimization']['emission_limit']['value'] = 0

        #change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath


        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        #solving
        pyhub.quick_solve()


# Run Chemelot case study emission limit
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    resultpath = "Z:/PyHub/PyHub_results/CM/RDS3_Chemelot_cluster_minE"
    json_filepath = Path(casepath) / "ConfigModel.json"


    TD = [10, 20, 40, 60, 100, 200, 0]



    maxemisions = 1304912.69
    elimit = [0.9, 0.8, 0.7, 0.68]

    for lim in elimit:
    # for nr in TD:
        with open(json_filepath) as json_file:
            model_config = json.load(json_file)

        # model_config['optimization']['typicaldays']['N']['value'] = nr
        # model_config['optimization']['objective']['value'] = 'emissions_minC'
        # model_config['optimization']['emission_limit']['value'] = 0

        model_config['optimization']['typicaldays']['N']['value'] = 10
        model_config['optimization']['objective']['value'] = 'costs_emissionlimit'
        model_config['optimization']['emission_limit']['value'] = lim * maxemisions


        # change save options
        model_config['reporting']['save_summary_path']['value'] = resultpath
        model_config['reporting']['save_path']['value'] = resultpath

        # Write the updated JSON data back to the file
        with open(json_filepath, 'w') as json_file:
            json.dump(model_config, json_file, indent=4)

        # Construct and solve the model
        pyhub = ModelHub()
        pyhub.read_data(casepath)

        pyhub.data.model_config['reporting']['case_name']['value'] = 'elimit' + str(int(round(lim*100)))
        pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

        # # add casename based on resolution
        # if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
        #     pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
        # else:
        #     pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(
        #         pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

        # solving
        pyhub.quick_solve()

# Add values of (part of) the parameters and variables to the summary file
# summarypath = Path(resultpath) / "Summary.xlsx"
# add_values_to_summary(summarypath)
