import os
from pathlib import Path
import h5py
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, gridspec

from adopt_net0 import extract_datasets_from_h5group

def fetch_and_process_data_production(
    result_folder,
    data_to_excel_path_olefins,
    data_to_excel_path_ammonia,
    tec_mapping,
    categories,
    combined_categories,  # FIXED unpacking: now a dict directly
    nr_iterations,
    location,
    ambition
):
    # Ensure combined_categories is not wrapped in a tuple
    if isinstance(combined_categories, tuple):
        combined_categories = combined_categories[0]

    # Combine all unique categories for the production tables
    all_categories = list(categories.keys()) + list(combined_categories.keys())

    # Initialize result containers
    olefin_results = []
    ammonia_results = []

    for i in range(nr_iterations + 1):
        if i == 0:
            iteration = "Standalone"
            iteration_folder = Path("Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/") / ambition
        else:
            iteration = f"Iteration_{i}"
            iteration_folder = Path(result_folder) / iteration

        columns = pd.MultiIndex.from_product(
            [[iteration], ['2030', '2040', '2050']],
            names=["Iteration", "Interval"]
        )

        # Initialize full production dataframe
        result_data = pd.DataFrame(0.0, index=tec_mapping.keys(), columns=columns)

        # Production per category
        production_sum_olefins = pd.DataFrame(0.0, index=all_categories, columns=columns)
        production_sum_ammonia = pd.DataFrame(0.0, index=all_categories, columns=columns)

        # read summary data
        summarypath = os.path.join(iteration_folder, "Summary.xlsx")

        try:
            summary_results = pd.read_excel(summarypath)
        except FileNotFoundError:
            print(f"Warning: Summary file not found for {iteration}")
            continue

        for interval in result_data.columns.levels[1]:
            for case in summary_results['case']:
                if pd.notna(case) and interval in case:
                    h5_path = Path(summary_results[summary_results['case'] == case].iloc[0][
                                       'time_stamp']) / "optimization_results.h5"
                    if h5_path.exists():
                        with h5py.File(h5_path, "r") as hdf_file:
                            tec_operation = extract_datasets_from_h5group(
                                hdf_file["operation/technology_operation"])
                            tec_operation = {k: v for k, v in tec_operation.items() if len(v) >= 8670}
                            df_tec_operation = pd.DataFrame(tec_operation)

                            for tec in tec_mapping.keys():
                                para = tec_mapping[tec][2] + "_output"
                                if (interval, location, tec, para) in df_tec_operation:
                                    output_car = df_tec_operation[interval, location, tec, para]

                                    if tec in ['CrackerFurnace', 'MPW2methanol', 'SteamReformer',
                                               'Biomass2methanol'] and (
                                            interval, location, tec, 'CO2captured_output') in df_tec_operation:
                                        numerator = df_tec_operation[
                                            interval, location, tec, 'CO2captured_output'].sum()
                                        denominator = (
                                                df_tec_operation[
                                                    interval, location, tec, 'CO2captured_output'].sum()
                                                + df_tec_operation[interval, location, tec, 'emissions_pos'].sum()
                                        )

                                        frac_CC = numerator / denominator if (
                                                denominator > 1 and numerator > 1) else 0

                                        frac_CC = frac_CC / 0.9

                                        tec_CC = tec + "_CC"
                                        result_data.loc[tec, (iteration, interval)] = sum(
                                            output_car) * (1 - frac_CC)
                                        result_data.loc[tec_CC, (iteration, interval)] = sum(
                                            output_car) * frac_CC
                                    else:
                                        result_data.loc[tec, (iteration, interval)] = sum(output_car)

                                tec_existing = tec + "_existing"
                                if (interval, location, tec_existing, para) in df_tec_operation:
                                    output_car = df_tec_operation[interval, location, tec_existing, para]

                                    if tec in ['CrackerFurnace', 'MPW2methanol', 'SteamReformer'] and (
                                            interval, location, tec_existing,
                                            'CO2captured_output') in df_tec_operation:
                                        numerator = df_tec_operation[
                                            interval, location, tec_existing, 'CO2captured_output'].sum()
                                        denominator = (
                                                df_tec_operation[
                                                    interval, location, tec_existing, 'CO2captured_output'].sum()
                                                + df_tec_operation[
                                                    interval, location, tec_existing, 'emissions_pos'].sum()
                                        )

                                        frac_CC = numerator / denominator if (
                                                denominator > 1 and numerator > 1) else 0

                                        frac_CC = frac_CC / 0.9

                                        tec_CC = tec + "_CC"
                                        result_data.loc[tec, (iteration, interval)] += sum(
                                            output_car) * (1 - frac_CC)
                                        result_data.loc[tec_CC, (iteration, interval)] += sum(
                                            output_car) * frac_CC
                                    else:
                                        result_data.loc[tec, (iteration, interval)] += sum(output_car)

                        # Define tech categories
                        tech_by_feedstock = {
                            'methane': ['SteamReformer', 'SteamReformer_CC', 'WGS_m'],
                            'naphtha': ['CrackerFurnace', 'CrackerFurnace_CC', 'CrackerFurnace_Electric']
                        }

                        # Check if any of the technologies are active
                        if any(result_data.loc[tech, (iteration, interval)] > 0
                               for techs in tech_by_feedstock.values() for tech in techs):

                            with h5py.File(h5_path, "r") as hdf_file:
                                ebalance = extract_datasets_from_h5group(hdf_file["operation/energy_balance"])
                                df_ebalance = pd.DataFrame(ebalance)

                                for feedstock, techs in tech_by_feedstock.items():
                                    fossil_key = (interval, location, feedstock, 'import')
                                    bio_key = (interval, location, f"{feedstock}_bio", 'import')

                                    tot_fossil = sum(df_ebalance.get(fossil_key, 0))
                                    tot_bio = sum(df_ebalance.get(bio_key, 0))

                                    if any(result_data.loc[tech, (iteration, interval)] > 0 for tech in
                                           techs) and tot_bio > 0:
                                        frac_bio = tot_bio / (tot_fossil + tot_bio) if (tot_fossil + tot_bio) > 0 else 0

                                        for tech in techs:
                                            prod = result_data.loc[tech, (iteration, interval)]
                                            bio_tech = f"{tech}_bio"
                                            result_data.loc[tech, (iteration, interval)] = prod * (1 - frac_bio)
                                            result_data.loc[bio_tech, (iteration, interval)] = prod * frac_bio

                    for tech, (product, category, feedstock, emission_factor) in tec_mapping.items():
                        if category not in production_sum_olefins.index and product == "Olefin":
                            production_sum_olefins.loc[category] = 0.0
                        if category not in production_sum_ammonia.index and product == "Ammonia":
                            production_sum_ammonia.loc[category] = 0.0

                        for interval in ['2030', '2040', '2050']:
                            value = result_data.loc[tech, (iteration, interval)]
                            if product == "Olefin":
                                production_sum_olefins.loc[category, (iteration, interval)] += value
                            elif product == "Ammonia":
                                production_sum_ammonia.loc[category, (iteration, interval)] += value

        olefin_results.append(production_sum_olefins)
        ammonia_results.append(production_sum_ammonia)

    production_sum_olefins = pd.concat(olefin_results, axis=1)
    production_sum_olefins.to_excel(data_to_excel_path_olefins)
    production_sum_ammonia = pd.concat(ammonia_results, axis=1)
    production_sum_ammonia.to_excel(data_to_excel_path_ammonia)


def main():
    #Define cluster ambition and number of iteration
    nr_iterations = 5
    flag_cluster_ambition = "Scope1-3"

    # Add basepath
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_to_excel_path1 = os.path.join(datapath, "Plotting", f"production_shares_olefins_{flag_cluster_ambition}.xlsx")
    data_to_excel_path2 = os.path.join(datapath, "Plotting", f"production_shares_ammonia_{flag_cluster_ambition}.xlsx")
    basepath_results = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/" + flag_cluster_ambition
    result_folder = basepath_results + "/Results_model_linking_20250806_11_36"

    tec_mapping = {
        "CrackerFurnace": ("Olefin", "Conventional", "olefins", 0.439),
        "CrackerFurnace_bio": ("Olefin", "Conventional + Bio-based feedstock", "olefins", 0.439),
        "CrackerFurnace_CC": ("Olefin", "Carbon Capture", "olefins", 0.439),
        "CrackerFurnace_CC_bio": ("Olefin", "Conventional + Bio-based feedstock with CC", "olefins", 0.439),
        "CrackerFurnace_Electric": ("Olefin", "Electrification", "olefins", 0.439),
        "CrackerFurnace_Electric_bio": ("Olefin", "Electrification + Bio-based", "olefins", 0.439),
        "SteamReformer": ("Ammonia", "Conventional", "HBfeed", 0.168),
        "SteamReformer_bio": ("Ammonia", "Conventional + Bio-based feedstock", "HBfeed", 0.168),
        "SteamReformer_CC": ("Ammonia", "Carbon Capture", "HBfeed", 0.168),
        "SteamReformer_CC_bio": ("Ammonia", "Conventional + Bio-based feedstock with CC", "HBfeed", 0.168),
        "WGS_m": ("Ammonia", "Electrification", "hydrogen", 0.168),
        "WGS_m_bio": ("Ammonia", "Electrification + Bio-based feedstock", "hydrogen", 0.168),
        "AEC": ("Ammonia", "Water electrolysis", "hydrogen", 0.168),
        "RWGS": ("Olefin", r"CO$_2$ utilization", "syngas", 0.270),
        "DirectMeOHsynthesis": ("Olefins", r"CO$_2$ utilization", "methanol", 0.328),
        "EDH": ("Olefin", "Bio-based feedstock", "ethylene", 1),
        "PDH": ("Olefin", "Bio-based feedstock", "propylene", 1),
        "MPW2methanol": ("Olefin", "Plastic waste recycling", "methanol", 0.328),
        "MPW2methanol_CC": ("Olefin", "Plastic waste recycling with CC", "methanol", 0.328),
        "CO2electrolysis": ("Olefin", r"CO$_2$ utilization", "ethylene", 1),
        "Biomass2methanol": ("Olefin", "Bio-based feedstock", "methanol", 0.328),
        "Biomass2methanol_CC": ("Olefin", "Bio-based feedstock with CC", "methanol", 0.328),
    }

    categories = {
        "Conventional": '#8C8B8B',
        "Carbon Capture": '#3E7EB0',
        "Electrification": '#E9E46D',
        "Water electrolysis": '#EABF37',
        r"CO$_2$ utilization": '#E18826',
        "Bio-based feedstock": '#84AA6F',
        "Bio-based feedstock with CC": '#088A01',
        "Plastic waste recycling": '#B475B2',
        "Plastic waste recycling with CC": '#533A8C',
    }

    combined_categories = {
        "Electrification + Bio-based feedstock": ("Electrification", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock": ("Conventional", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock with CC": ("Conventional", "Bio-based feedstock with CC"),
    }

    fetch_and_process_data_production(result_folder, data_to_excel_path1, data_to_excel_path2,
                                          tec_mapping, categories, combined_categories, nr_iterations, 'Zeeland',
                                          flag_cluster_ambition)



if __name__ == "__main__":
    main()



