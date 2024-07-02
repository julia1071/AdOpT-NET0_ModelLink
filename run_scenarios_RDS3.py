import json
from pathlib import Path
import adopt_net0.data_preprocessing as dp
from adopt_net0.modelhub import ModelHub
from adopt_net0.result_management.read_results import add_values_to_summary


#Run Chemelot cluster case
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    resultpath = "Z:/PyHub/PyHub_results/CM/Cluster_integration/Chemelot_cluster"
    json_filepath = Path(casepath) / "ConfigModel.json"


    with open(json_filepath) as json_file:
        model_config = json.load(json_file)

    model_config['optimization']['typicaldays']['N']['value'] = 20
    model_config['optimization']['objective']['value'] = 'pareto'
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

    pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

    #add casename based on resolution
    if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
    else:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

    #solving
    pyhub.quick_solve()


#Run Chemelot ammonia case
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_ammonia"
    resultpath = "Z:/PyHub/PyHub_results/CM/Cluster_integration/Chemelot_ammonia"
    json_filepath = Path(casepath) / "ConfigModel.json"


    with open(json_filepath) as json_file:
        model_config = json.load(json_file)

    model_config['optimization']['typicaldays']['N']['value'] = 20
    model_config['optimization']['objective']['value'] = 'pareto'
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

    pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

    #add casename based on resolution
    if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
    else:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

    #solving
    pyhub.quick_solve()


#Run Chemelot ethylene
execute = 0

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_ethylene"
    resultpath = "Z:/PyHub/PyHub_results/CM/Cluster_integration/Chemelot_ethylene"
    json_filepath = Path(casepath) / "ConfigModel.json"


    with open(json_filepath) as json_file:
        model_config = json.load(json_file)

    model_config['optimization']['typicaldays']['N']['value'] = 20
    model_config['optimization']['objective']['value'] = 'pareto'
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

    pyhub.data.model_config['solveroptions']['mipfocus']['value'] = 1

    #add casename based on resolution
    if pyhub.data.model_config['optimization']['typicaldays']['N']['value'] == 0:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'fullres'
    else:
        pyhub.data.model_config['reporting']['case_name']['value'] = 'TD' + str(pyhub.data.model_config['optimization']['typicaldays']['N']['value'])

    #solving
    pyhub.quick_solve()



