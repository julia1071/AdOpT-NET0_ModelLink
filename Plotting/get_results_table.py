import os
import h5py
import numpy as np
import pandas as pd

from pathlib import Path
from adopt_net0 import extract_datasets_from_h5group

#options
nr_iterations = 5
ambition = "Scope1-3"
location = "Zeeland"

# Define paths
basepath_results = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/" + ambition
result_folder = basepath_results + "/Results_model_linking_20250806_11_36"
# result_folder = basepath_results + "/Results_model_linking_20250808_17_50"
basepath_plots = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_to_excel_path = os.path.join(basepath_plots, "Plotting", f"result_data_long_{ambition}.xlsx")


# Initialize an empty dictionary to collect DataFrame results
all_results = []

for iteration in range(nr_iterations + 1):
    if iteration == 0:
        iteration_name = "Standalone"
        iteration_folder = Path("Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/") / ambition
    else:
        iteration_name = "Iteration_" + str(iteration)
        iteration_folder = Path(result_folder) / iteration_name

    columns = pd.MultiIndex.from_product(
        [[iteration_name], ['2030', '2040', '2050']],
        names=["Iteration", "Interval"]
    )

    # Define the index rows
    index = ["path", "costs_obj_interval", "sunk_costs", "costs_tot_interval", "costs_tot_cumulative", "emissions_net"]

    # Create the DataFrame for this result type with NaN values
    result_data = pd.DataFrame(np.nan, index=index, columns=columns)

    # Fill the path column using a loop
    summarypath = os.path.join(iteration_folder, "Summary.xlsx")

    try:
        summary_results = pd.read_excel(summarypath)
    except FileNotFoundError:
        print(f"Warning: Summary file not found for {iteration_name}")
        continue

    tec_costs = {}
    total_costs = {}
    for case in summary_results['case']:
        for i, interval in enumerate(result_data.columns.levels[1]):
            if pd.notna(case) and interval in case:
                h5_path = Path(summary_results.loc[summary_results['case'] == case, 'time_stamp'].iloc[
                                   0]) / "optimization_results.h5"
                result_data.at["path", (iteration_name, interval)] = h5_path
                result_data.loc["costs_obj_interval", (iteration_name, interval)] = \
                    summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[0]
                result_data.loc["emissions_net", (iteration_name, interval)] = \
                    summary_results.loc[summary_results['case'] == case, 'emissions_net'].iloc[0]
                tec_costs[interval] = summary_results.loc[summary_results['case'] == case, 'cost_capex_tecs'].iloc[0]
                total_costs[interval] = summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[
                    0]

                #Calculate sunk costs and cumulative costs for brownfield
                prev_interval = result_data.columns.levels[1][i - 1]
                if interval == '2030':
                    result_data.loc["costs_tot_interval", (iteration_name, interval)] = \
                        summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[0]
                if interval == '2040':
                    result_data.loc["sunk_costs", (iteration_name, interval)] = tec_costs[prev_interval]
                    result_data.loc["costs_tot_interval", (iteration_name, interval)] = tec_costs[prev_interval] + \
                                                                                        summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[0]
                if interval == '2050':
                    first_interval = result_data.columns.levels[1][i - 2]
                    result_data.loc["sunk_costs", (iteration_name, interval)] = tec_costs[
                        prev_interval] + tec_costs[first_interval]
                    result_data.loc["costs_tot_interval", (iteration_name, interval)] = tec_costs[prev_interval] + \
                                                                                        + tec_costs[first_interval] + summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[0]
                    result_data.loc["costs_tot_cumulative", (iteration_name, interval)] = sum(
                        total_costs.values()) * 10 + tec_costs[prev_interval] * 10 + tec_costs[first_interval] * 10

                # Function to get capacities for different technologies.
                if h5_path.exists():
                    with h5py.File(h5_path, "r") as hdf_file:
                        nodedata = extract_datasets_from_h5group(hdf_file["design/nodes"])
                        df_nodedata = pd.DataFrame(nodedata)

                        for tec in df_nodedata.columns.levels[2]:
                            output_name = f'size_{tec}'
                            if (interval, location, tec, 'size') in df_nodedata.columns:
                                result_data.loc[output_name, (iteration_name, interval)] = \
                                    df_nodedata[(interval, location, tec, 'size')].iloc[0]
                            else:
                                result_data.loc[output_name, (iteration_name, interval)] = 0

                            if any(tec.startswith(base) for base in ['CrackerFurnace', 'MPW2methanol', 'SteamReformer',
                                           'Biomass2methanol']):
                                tec_operation = extract_datasets_from_h5group(
                                    hdf_file["operation/technology_operation"])
                                tec_operation = {k: v for k, v in tec_operation.items() if len(v) >= 8670}
                                df_tec_operation = pd.DataFrame(tec_operation)
                                if (interval, location, tec, 'CO2captured_output') in df_tec_operation:
                                    numerator = df_tec_operation[
                                        interval, location, tec, 'CO2captured_output'].sum()
                                    denominator = (
                                            df_tec_operation[
                                                interval, location, tec, 'CO2captured_output'].sum()
                                            + df_tec_operation[interval, location, tec, 'emissions_pos'].sum()
                                    )

                                    frac_CC = numerator / denominator if (denominator > 1 and numerator > 1) else 0

                                    tec_CC = "size_" + tec + "_CC"
                                    if tec_CC not in result_data.index:
                                        result_data.loc[tec_CC] = pd.Series(dtype=float)
                                    result_data.loc[tec_CC, (iteration_name, interval)] = frac_CC

                        ebalance = extract_datasets_from_h5group(hdf_file["operation/energy_balance"])
                        df_ebalance = pd.DataFrame(ebalance)
                        cars_at_node = df_ebalance[interval, location].columns.droplevel([1]).unique()

                        for car in cars_at_node:
                            parameters = ["import", "export"]
                            for para in parameters:
                                output_name = f"{car}/{para}_max"
                                if (interval, location, car, para) in df_ebalance.columns:
                                    car_output = df_ebalance[interval, location, car, para]
                                    result_data.loc[output_name, (iteration_name, interval)] = max(
                                        car_output)
                                else:
                                    result_data.loc[output_name, (iteration_name, interval)] = 0

    # # Store results for this result_type
    all_results.append(result_data)

# Concatenate all result types into a single DataFrame
final_result_data = pd.concat(all_results, axis=1)

# Save to Excel (optional)
final_result_data.to_excel(data_to_excel_path)
