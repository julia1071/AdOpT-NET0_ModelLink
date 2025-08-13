import os
import json
from datetime import datetime

from run_IESA_from_python import run_IESA_change_name_files
from get_results_IESA import get_results_IESA_dict, convert_IESA_to_cluster_dict
from run_adopt import run_adopt
from get_results_cluster import get_results_cluster_technology_output_dict
from extract_and_apply_cc_fractions import extract_and_apply_cc_fractions
from merge_and_group_technologies import merge_and_group_technologies
from extract_and_apply_import_share_bio import extract_and_apply_import_bio_ratios
from map_techs_to_ID import map_techs_to_ID
from update_and_clear_input_file_IESA import update_input_file_IESA, clear_input_file_IESA
from convergence_criteria import compare_cluster_outputs, get_cluster_epsilon
from utils import convert_ndarrays_to_lists

import config_model_linking as cfg


def model_linking(max_iterations, e, scope3_on, save_extension_link):
    i = 1
    inputs_cluster = {}
    outputs_cluster = {}
    epsilon = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H_%M")
    map_name_cluster = cfg.cluster_result_folder / save_extension_link / f"Results_model_linking_{timestamp}"
    map_name_IESA = cfg.IESA_result_folder / save_extension_link / f"Results_model_linking_{timestamp}"
    os.makedirs(map_name_cluster, exist_ok=True)
    os.makedirs(map_name_IESA, exist_ok=True)
    while True:
        #First clear the input file for iteration 1
        if i == 1:
            clear_input_file_IESA(
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                tech_to_id=cfg.tech_to_id
            )

        #Run IESA
        results_path_IESA = run_IESA_change_name_files(iteration=i,
                                                       map_name_IESA=map_name_IESA)

        #Read results into a dictionary
        results_IESA_dict = get_results_IESA_dict(results_file_path=results_path_IESA)

        #Convert dictionary to correct cluster input units
        cluster_linked_input_dict = convert_IESA_to_cluster_dict(results_IESA_dict=results_IESA_dict,
                                                                 results_path_IESA=results_path_IESA)

        #Run cluster model
        iteration_path = map_name_cluster / f"Iteration_{i}"
        solution_cluster = run_adopt(case_path=cfg.cluster_case_path,
                                     iteration_path=iteration_path,
                                     cluster_input_dict=cluster_linked_input_dict,
                                     scope3_on=scope3_on)

        #Extract technology sizes from cluster model and save in dict
        tech_output_dict = get_results_cluster_technology_output_dict(adopt_hub=solution_cluster)

        #Update dict to include CC fractions of technologies
        tech_dict_updated_cc = extract_and_apply_cc_fractions(adopt_hub=solution_cluster,
                                                              tech_output_dict=tech_output_dict)

        #Merge new with existing technologies and group technologies for use in IESA
        merged_tech_output_dict = merge_and_group_technologies(tech_dict=tech_dict_updated_cc)

        #Update dict to include fraction of bio based technology
        tech_dict_updated_bio = extract_and_apply_import_bio_ratios(adopt_hub=solution_cluster,
                                                                    tech_output_dict=merged_tech_output_dict)

        #Map techs to ID as final step to update IESA
        updates_to_IESA = map_techs_to_ID(tech_dict_updated_bio, cfg.tech_to_id)
        print(r"The following updates are inserted into IESA-Opt:")
        print(updates_to_IESA)

        outputs_cluster[f"iteration_{i}"] = updates_to_IESA
        inputs_cluster[f"iteration_{i}"] = cluster_linked_input_dict
        if i > 1:
            epsilon[f"iteration_{i}"] = get_cluster_epsilon(outputs_cluster, i)

        if compare_cluster_outputs(epsilon, i, e) or i == max_iterations:
            print(f"✅ Model linking is done after {i} iterations.")

            # Save outputs_cluster to JSON
            output_file = map_name_cluster / "outputs_cluster.json"
            input_file = map_name_cluster / "inputs_cluster.json"
            epsilon_file = map_name_cluster / "epsilons.json"

            with open(input_file, "w") as f:
                json.dump(inputs_cluster, f, indent=4)

            with open(output_file, "w") as f:
                json.dump(convert_ndarrays_to_lists(outputs_cluster), f, indent=4)

            with open(epsilon_file, "w") as f:
                json.dump(epsilon, f, indent=4)

            print(f"📝 Saved inputs and outputs of the cluster model")

            break  # ← loop ends here
        else:
            update_input_file_IESA(
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                update_data=updates_to_IESA,
                tech_to_id=cfg.tech_to_id
            )

            # Save outputs_cluster to JSON
            output_file = map_name_cluster / "outputs_cluster.json"
            input_file = map_name_cluster / "inputs_cluster.json"
            epsilon_file = map_name_cluster / "epsilons.json"

            with open(input_file, "w") as f:
                json.dump(inputs_cluster, f, indent=4)

            with open(output_file, "w") as f:
                json.dump(convert_ndarrays_to_lists(outputs_cluster), f, indent=4)

            with open(epsilon_file, "w") as f:
                json.dump(epsilon, f, indent=4)

            print(f"📝 Saved inputs and outputs of the cluster model")

            print(f"Linking iteration {i} is executed")
            i += 1
            print(f"The next iteration, iteration {i} is started")


# run for scope 1-3
model_linking(max_iterations=cfg.max_iterations, e=cfg.e, scope3_on=1, save_extension_link='Scope1-3')

# run for scope 1-2
model_linking(max_iterations=cfg.max_iterations, e=cfg.e, scope3_on=0, save_extension_link='Scope1-2')
