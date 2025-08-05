import os
from pathlib import Path
import h5py
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, gridspec

from adopt_net0 import extract_datasets_from_h5group

#Add basepath
DATAPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_TO_EXCEL_PATH1 = os.path.join(DATAPATH, "Plotting", "production_shares_olefins.xlsx")
DATA_TO_EXCEL_PATH2 = os.path.join(DATAPATH, "Plotting", "production_shares_ammonia.xlsx")


def fetch_and_process_data_production(result_folder, data_to_excel_path_olefins, data_to_excel_path_ammonia,
                                      tec_mapping, categories, nr_iterations, location, ambition):
    olefin_results = []
    ammonia_results = []

    for i in range(nr_iterations+1):
        if i == 0:
            iteration = "Standalone"
            iteration_folder = Path("Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Standalone/") / ambition
        else:
            iteration = "Iteration_" + str(i)
            iteration_folder = Path(result_folder) / iteration

        columns = pd.MultiIndex.from_product(
            [[iteration], ['2030', '2040', '2050']],
            names=["Iteration", "Interval"]
        )

        result_data = pd.DataFrame(0.0, index=tec_mapping.keys(), columns=columns)
        production_sum_olefins = pd.DataFrame(0.0, index=categories.keys(), columns=columns)
        production_sum_ammonia = pd.DataFrame(0.0, index=categories.keys(), columns=columns)

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

                                        tec_CC = tec + "_CC"
                                        result_data.loc[tec, (iteration, interval)] += sum(
                                            output_car) * (1 - frac_CC)
                                        result_data.loc[tec_CC, (iteration, interval)] += sum(
                                            output_car) * frac_CC
                                    else:
                                        result_data.loc[tec, (iteration, interval)] += sum(output_car)

                        for tec in tec_mapping.keys():
                            if tec_mapping[tec][0] == 'Olefin':
                                olefin_production = result_data.loc[tec, (iteration, interval)] * \
                                                    tec_mapping[tec][3]
                                production_sum_olefins.loc[
                                    tec_mapping[tec][1], (iteration, interval)] += olefin_production
                            elif tec_mapping[tec][0] == 'Ammonia':
                                ammonia_production = result_data.loc[tec, (iteration, interval)] * \
                                                     tec_mapping[tec][3]
                                production_sum_ammonia.loc[
                                    tec_mapping[tec][1], (iteration, interval)] += ammonia_production

        olefin_results.append(production_sum_olefins)
        ammonia_results.append(production_sum_ammonia)

    production_sum_olefins = pd.concat(olefin_results, axis=1)
    production_sum_olefins.to_excel(data_to_excel_path_olefins)
    production_sum_ammonia = pd.concat(ammonia_results, axis=1)
    production_sum_ammonia.to_excel(data_to_excel_path_ammonia)


def plot_production_shares(production_sum_olefins, production_sum_ammonia, categories, intervals, iterations,
                           include_costs=False, separate=False, cost_data=None, total_cost=False):
    mpl.rcParams['font.family'] = 'serif'

    group_size = len(iterations)
    total_bars = group_size * len(intervals)
    x = np.arange(total_bars)
    bar_width = 0.6 / group_size

    def normalize(df):
        df = df.sort_index(axis=1)  # Fix PerformanceWarning
        df_norm = df.copy()
        for interval in intervals:
            for iteration in iterations:
                col = (iteration, interval)
                if col in df.columns:
                    total = df.loc[:, col].sum()
                    if total > 0:
                        df_norm.loc[:, col] = df.loc[:, col] / total
                    else:
                        df_norm.loc[:, col] = 0
        return df_norm

    production_sum_olefins = normalize(production_sum_olefins)
    production_sum_ammonia = normalize(production_sum_ammonia)

    n_rows = 3 if (include_costs and separate) else 2
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 9 if n_rows == 3 else 6), sharex=True)
    axes = axes if isinstance(axes, np.ndarray) else [axes]

    def make_stacked_bars(ax, df, product):
        for idx_interval, interval in enumerate(intervals):
            for idx_iter, iteration in enumerate(iterations):
                bar_index = idx_interval * group_size + idx_iter
                bottom = 0
                for category, color in categories.items():
                    val = df.loc[category, (iteration, interval)] if (iteration, interval) in df.columns else 0
                    ax.bar(x[bar_index], val, bar_width, bottom=bottom, color=color,
                           label=category if bottom == 0 else "")
                    bottom += val
        ax.set_ylabel(f"Share of total production\n{product}")
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.5, total_bars - 0.5)
        ax.spines[['top', 'right']].set_visible(False)

    make_stacked_bars(axes[0], production_sum_olefins, "olefins")
    make_stacked_bars(axes[1], production_sum_ammonia, "ammonia")

    # Common x-ticks and interval lines
    xtick_labels = []
    for interval in intervals:
        for i in range(group_size):
            xtick_labels.append("Standalone" if i == 0 else f"Iteration {i}")

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(xtick_labels, rotation=45, ha='right')

    for i in range(1, len(intervals)):
        xpos = i * group_size - 0.5
        for ax in axes[:2]:  # Don't add lines to cost axis
            ax.axvline(x=xpos, color='gray', linestyle='dashed', linewidth=1)

    for i, interval in enumerate(intervals):
        mid = (i * group_size + (i + 1) * group_size - 1) / 2
        axes[0].text(mid, 1.05, interval, ha='center', va='bottom', fontsize=14)

    # Add costs if applicable
    if include_costs and cost_data is not None:
        if not total_cost:
            cost_data = cost_data / 2_901_310  # Convert to €/t

        if separate:
            ax_cost = axes[2]
            ax_cost.bar(x, cost_data, color='gray', width=0.8, label='Production cost')
            ax_cost.set_ylabel("Total cluster cost [€/t]")
            ax_cost.set_ylim(0, max(cost_data) * 1.2)
            ax_cost.spines[['top', 'right']].set_visible(False)
            ax_cost.spines['left'].set_color('navy')
            ax_cost.spines['left'].set_linewidth(1)
            ax_cost.legend(loc='upper right', fontsize=9)
        else:
            ax2 = axes[1].twinx()
            ax2.plot(x, cost_data, 'o', color='black', markersize=4, label='Production cost')
            ax2.set_ylabel("Total cluster cost [€/t]", color='black', loc='center')
            ax2.yaxis.set_label_position("right")
            ax2.yaxis.tick_right()
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_color('navy')
            ax2.spines['right'].set_linewidth(1)
            ax2.set_ylim(0, max(cost_data) * 1.2)
            ax2.legend(loc='upper right', fontsize=9)

    # Legend & layout
    handles, labels = axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(unique.values(), unique.keys(), loc='lower center', ncol=6, fontsize=10,
               bbox_to_anchor=(0.5, 0.01))
    plt.subplots_adjust(hspace=0.3, bottom=0.2, left=0.08, right=0.92)

    return plt



def main():
    #Define cluster ambition and number of iteration
    nr_iterations = 1
    flag_cluster_ambition = "Scope1-3"
    include_prod_costs = False
    separate = False
    intervals = ['2030', '2040', '2050']
    iterations = ['Standalone'] + [f'Iteration_{i}' for i in range(1, nr_iterations + 1)]

    # Define paths
    basepath_results = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/" + flag_cluster_ambition
    result_folder = basepath_results + "/Results_model_linking_20250803_19_05"
    plot_folder = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/IterationBars_" + flag_cluster_ambition
    cost_data_excel = os.path.join(DATAPATH, "Plotting", f"result_data_long_{flag_cluster_ambition}.xlsx")

    tec_mapping = {
        "CrackerFurnace": ("Olefin", "Conventional", "olefins", 0.439),
        "CrackerFurnace_CC": ("Olefin", "Carbon Capture", "olefins", 0.439),
        "CrackerFurnace_Electric": ("Olefin", "Electrification", "olefins", 0.439),
        "SteamReformer": ("Ammonia", "Conventional", "HBfeed", 0.168),
        "SteamReformer_CC": ("Ammonia", "Carbon Capture", "HBfeed", 0.168),
        "WGS_m": ("Ammonia", "Electrification", "hydrogen", 0.168),
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
        "Bio-based feedstock with CC": '#013220',
        "Plastic waste recycling": '#B475B2',
        "Plastic waste recycling with CC": '#533A8C',
    }

    get_data = 0

    if get_data == 1:
        fetch_and_process_data_production(result_folder, DATA_TO_EXCEL_PATH1, DATA_TO_EXCEL_PATH2,
                                          tec_mapping, categories, nr_iterations, 'Zeeland',
                                          flag_cluster_ambition)

    production_sum_olefins = pd.read_excel(DATA_TO_EXCEL_PATH1, index_col=0, header=[0, 1])
    production_sum_ammonia = pd.read_excel(DATA_TO_EXCEL_PATH2, index_col=0, header=[0, 1])

    if include_prod_costs:
        df_costs = pd.read_excel(cost_data_excel, header=[0, 1], index_col=0)
        if 'costs_obj_interval' not in df_costs.index:
            raise KeyError("Row 'costs_obj_interval' not found in cost Excel")
        cost_values = df_costs.loc['costs_obj_interval']
    else:
        cost_values = None

    plt_obj = plot_production_shares(production_sum_olefins=production_sum_olefins,
                                     production_sum_ammonia=production_sum_ammonia,
                                     categories=categories,
                                     intervals=intervals,
                                     iterations=iterations,
                                     include_costs=include_prod_costs,
                                     separate=separate,
                                     cost_data=cost_values,
                                     total_cost=False)

    #saving options
    save = "no"
    if save == "pdf":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    elif save == "svg":
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
    elif save == "both":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')


    plt.show()



if __name__ == "__main__":
    main()



