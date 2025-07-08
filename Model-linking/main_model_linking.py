import os
import sys
from pathlib import Path
import json
from datetime import datetime

from run_IESA_from_python import run_IESA_change_name_files
from extract_data_IESA_multiple_headers import extract_data_IESA_multiple, convert_IESA_to_cluster_dict
from run_adopt import run_adopt
from get_results_cluster_dict_output import extract_technology_outputs
from extract_cc_fractions import extract_and_apply_cc_fractions
from merge_existing_new_techs import merge_existing_and_new_techs
from combine_tech_outputs import combine_tech_outputs
from extract_import_share_naphtha import extract_import_bio_ratios_naphtha
from split_technologies_bio import apply_bio_splitting
from map_techs_to_ID import map_techs_to_ID
from update_input_file_IESA import update_input_file_IESA
from clear_input_file_IESA import clear_input_file_IESA
from compare_outputs import compare_outputs

from config_model_linking import *

def model_linking(max_iterations):
    i = 1
    inputs_cluster = {}
    outputs_cluster = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H_%M")
    map_name_cluster = cluster_result_folder / f"Results_model_linking_{timestamp}"
    map_name_IESA = IESA_result_folder / f"Results_model_linking_simplified_{timestamp}"
    os.makedirs(map_name_cluster, exist_ok=True)
    os.makedirs(map_name_IESA, exist_ok=True)
    while True:
        #Run IESA
        results_path_IESA = run_IESA_change_name_files(iteration=i,
                                                       command=command,
                                                       original_name_input=original_filename_input_IESA,
                                                       original_name_output=original_filename_output_IESA,
                                                       input_basename=basename_new_input_IESA,
                                                       output_basename=basename_new_output_IESA,
                                                       map_name_IESA=map_name_IESA)

        #Read results into a dictionary
        results_IESA_dict = extract_data_IESA_multiple(results_file_path=results_path_IESA)

        #Convert dictionary to correct cluster input units
        cluster_linked_input_dict = convert_IESA_to_cluster_dict(results_IESA_dict=results_IESA_dict,
                                                                 results_path_IESA=results_path_IESA)

        #Run cluster model
        iteration_path = map_name_cluster / f"Iteration_{i}"
        solution_cluster = run_adopt(case_path=cluster_case_path,
                                  iteration_path=iteration_path,
                                  cluster_input_dict=cluster_linked_input_dict)


        tech_output_dict = extract_technology_outputs(adopt_hub=solution_cluster)
        # print(r"The tech_size_dict created:")
        # print(tech_output_dict)

        tech_dict_updated_cc = extract_and_apply_cc_fractions(adopt_hub=solution_cluster, tech_output_dict=tech_output_dict)
        print(r"The updated_dict_cc created:")

        merged_tech_output_dict = merge_existing_and_new_techs(tech_dict=tech_dict_updated_cc)
        print(r"The merged_tech_output_dict created:")
        print(merged_tech_output_dict)
        combined_dict = combine_tech_outputs(merged_tech_output_dict, group_map)
        bio_ratios = extract_import_bio_ratios_naphtha(iteration_path, intervals, location)
        updated_dict_bio = apply_bio_splitting(combined_dict, bio_ratios, bio_tech_names, location)
        print(r"The updated_dict_bio created:")
        print(updated_dict_bio)
        updates = map_techs_to_ID(updated_dict_bio, tech_to_id)
        print(r"The following updates are inserted into IESA-Opt:")
        print(updates)

        outputs_cluster[f"iteration_{i}"] = updates
        inputs_cluster[f"iteration_{i}"] = cluster_linked_input_dict

        if compare_outputs(outputs_cluster, i, e) or i == max_iterations:
            print(f"✅ Model linking is done after {i} iterations.")

            # Save outputs_cluster to JSON
            output_file = map_name_cluster / "outputs_cluster.json"
            input_file = map_name_cluster / "inputs_cluster.json"

            with open(input_file, "w") as f:
                json.dump(inputs_cluster, f, indent=4)

            with open(output_file, "w") as f:
                json.dump(outputs_cluster, f, indent=4)

            print(f"📝 Saved inputs and outputs of the cluster model")

            clear_input_file_IESA(
                IESA_input_data_path,
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                tech_to_id=tech_to_id
                )
            break  # ← loop ends here
        else:
            update_input_file_IESA(
                IESA_input_data_path,
                sheet_name="Technologies",
                tech_id_col="A",
                tech_id_row_start=7,
                merged_row=2,
                header_row=5,
                merged_name="Minimum use in a year",
                update_data=updates,
                tech_to_id=tech_to_id
            )
            print(f"Linking iteration {i} is executed")
            i += 1
            print(f"The next iteration, iteration {i} is started")


model_linking(max_iterations=3)
