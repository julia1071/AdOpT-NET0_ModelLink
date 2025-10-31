import os
from matplotlib.patches import Patch
from pathlib import Path
import h5py
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, gridspec
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from adopt_net0 import extract_datasets_from_h5group

#Add basepath
basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def plot_production_shares(production_sum_olefins, production_sum_ammonia, categories, intervals, iterations,
                           include_costs=False, cost_data=None, total_cost=False, combined_categories=None):
    plt.rcParams.update({'font.family': 'serif', 'font.size': 12})

    group_size = len(iterations)
    total_bars = group_size * len(intervals)
    x = np.arange(total_bars)
    # bar_width = 1.5 / group_size    #change bar width here
    bar_width = 0.7

    def normalize(df):
        df = df.sort_index(axis=1)
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

    production_sum_ammonia = normalize(production_sum_ammonia)
    production_sum_olefins = normalize(production_sum_olefins)

    n_rows = 3 if include_costs else 2
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 9 if n_rows == 3 else 6), sharex=True)
    axes = axes if isinstance(axes, np.ndarray) else [axes]

    for ax in axes:
        ax.tick_params(axis='y', labelsize=12)
        ax.yaxis.label.set_size(16)

    def make_stacked_bars(ax, df, product):
        for idx_interval, interval in enumerate(intervals):
            for idx_iter, iteration in enumerate(iterations):
                bar_index = idx_interval * group_size + idx_iter
                bottom = 0
                for category, color in categories.items():
                    val = df.loc[category, (iteration, interval)] if (iteration, interval) in df.columns else 0
                    ax.bar(x[bar_index], val, bar_width, bottom=bottom, color=color, label=category if bottom == 0 else "")
                    bottom += val

                if combined_categories:
                    for comb_cat, (cat1, cat2) in combined_categories.items():
                        val = df.loc[comb_cat, (iteration, interval)] if (iteration, interval) in df.columns else 0
                        if val > 0:
                            hatch = '////'  # thicker pattern
                            facecolor = categories.get(cat1, 'grey')  # base fill
                            edgecolor = categories.get(cat2, 'black')  # second category defines hatch color
                            bar = ax.bar(x[bar_index], val, bar_width, bottom=bottom,
                                         color=facecolor, hatch=hatch, edgecolor=edgecolor,
                                         label=comb_cat if bottom == 0 else "")
                            bottom += val

        ax.set_ylabel(f"Share of {product}\nproduction")
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.5, total_bars - 0.5)
        ax.spines[['top', 'right']].set_visible(False)

    make_stacked_bars(axes[0], production_sum_ammonia, "ammonia")
    make_stacked_bars(axes[1], production_sum_olefins, "olefins")

    xtick_labels = []
    for interval in intervals:
        for i in range(group_size):
            xtick_labels.append("Standalone" if i == 0 else f"Iteration {i}")

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(xtick_labels, rotation=45, ha='right', fontsize=16)

    for i in range(1, len(intervals)):
        xpos = i * group_size - 0.5
        for ax in axes[:2]:
            ax.axvline(x=xpos, color='gray', linestyle='dashed', linewidth=1)

    for i, interval in enumerate(intervals):
        mid = (i * group_size + (i + 1) * group_size - 1) / 2
        axes[0].text(mid, 1.05, interval, ha='center', va='bottom', fontsize=18)

    if include_costs and cost_data is not None:
        # build new column order: for each interval, all iterations in order
        new_cols = []
        for interval in intervals:
            for iteration in iterations:
                if (iteration, interval) in cost_data.columns:
                    new_cols.append((iteration, interval))

        # reindex columns
        cost_data_ordered = cost_data.reindex(columns=pd.MultiIndex.from_tuples(new_cols))

        # Convert to €/t if not total_cost
        if not total_cost:
            cost_data_ordered = cost_data_ordered / 2_901_310

        # Labels and colors
        cost_labels = {
            "CAPEX": "CAPEX",
            "OPEX_fix": "Fixed OPEX",
            "OPEX_var": "Variable OPEX",
            "OPEX_emis": "Emission costs",
        }
        cost_colors = {
            "CAPEX": "#111F4A",  # darkest
            "OPEX_fix": "#355C7D",
            "OPEX_var": "#6C9BCF",
            "OPEX_emis": "#A9CFF7",  # lightest
        }

        # Flatten each row into a 1D array matching x positions
        cost_arrays = {
            row: pd.to_numeric(cost_data_ordered.loc[row].to_numpy().flatten(), errors="coerce")
            for row in ["CAPEX", "OPEX_fix", "OPEX_var", "OPEX_emis"]
            if row in cost_data_ordered.index
        }

        # Plot stacked bar chart
        ax_cost = axes[2]
        bottom = np.zeros_like(x, dtype=float)
        for key in ["CAPEX", "OPEX_fix", "OPEX_var", "OPEX_emis"]:
            if key not in cost_arrays:
                continue
            values = cost_arrays[key]
            ax_cost.bar(
                x, values, bottom=bottom,
                color=cost_colors[key], width=0.8,
                label=cost_labels[key]
            )
            bottom += values

        ax_cost.set_ylabel("Cluster production\ncost [€/t]")
        ax_cost.set_ylim(0, bottom.max() * 1.2)
        ax_cost.spines[['top', 'right']].set_visible(False)
        ax_cost.legend(loc='upper right', ncol=2, fontsize=12, bbox_to_anchor=(1, 1.1))

    # Final legend (remove duplicates)
    # handles, labels = axes[0].get_legend_handles_labels()
    # unique = dict(zip(labels, handles))
    # fig.legend(unique.values(), unique.keys(), loc='lower center', ncol=6, fontsize=10,
    #            bbox_to_anchor=(0.5, 0.01))

    # #legend from categories
    # legend_elements = [Patch(facecolor=color, label=label) for label, color in categories.items()]
    #
    # fig.legend(legend_elements, categories.keys(), loc='lower center', ncol=5, fontsize=10,
    #            bbox_to_anchor=(0.5, 0.01))
    #
    plt.subplots_adjust(hspace=0.2, bottom=0.16, left=0.10, right=0.92)

    return plt

def save_separate_legend(categories, filename="legend_short"):


        plt.rcParams.update({'font.family': 'serif', 'font.size': 16})
        fig, ax = plt.subplots(figsize=(7.5, 1))  # Adjust as needed

        handles = [mpatches.Patch(color=color, label=label)
                   for label, color in categories.items()]

        ax.axis('off')
        legend = fig.legend(handles=handles,
                            loc='center',
                            ncol=5,
                            frameon=False)

        plt.tight_layout()
        fig.savefig(
            os.path.join(basepath, "Plotting", "Plots_final",
                         f"{filename}.pdf"), format='pdf', bbox_inches='tight')
        fig.savefig(
            os.path.join(basepath, "Plotting", "Plots_final",
                         f"{filename}.svg"), format='svg', bbox_inches='tight')
        plt.close(fig)



def main():
    #Define cluster ambition and number of iteration
    IESA_fossilphaseout = 1
    nr_iterations = 2
    flag_cluster_ambition = "Scope1-2"
    include_prod_costs = True
    separate = True
    intervals = ['2030', '2040', '2050']
    iterations = ['Standalone'] + [f'Iteration_{i}' for i in range(1, nr_iterations + 1)]

    # Add basepath
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if IESA_fossilphaseout:
        data_to_excel_path1 = os.path.join(datapath, "Plotting", "Results_excels",
                                           f"production_shares_olefins_{flag_cluster_ambition}_FPO.xlsx")
        data_to_excel_path2 = os.path.join(datapath, "Plotting", "Results_excels",
                                           f"production_shares_ammonia_{flag_cluster_ambition}_FPO.xlsx")
        plot_folder = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/IterationBars_FPO_" + flag_cluster_ambition
        cost_data_excel = os.path.join(datapath, "Plotting", "Results_excels",
                                       f"result_data_long_{flag_cluster_ambition}_FPO.xlsx")
    else:
        data_to_excel_path1 = os.path.join(datapath, "Plotting", "Results_excels",
                                           f"production_shares_olefins_{flag_cluster_ambition}.xlsx")
        data_to_excel_path2 = os.path.join(datapath, "Plotting", "Results_excels",
                                           f"production_shares_ammonia_{flag_cluster_ambition}.xlsx")
        plot_folder = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/IterationBars_" + flag_cluster_ambition
        cost_data_excel = os.path.join(datapath, "Plotting", "Results_excels",
                                       f"result_data_long_{flag_cluster_ambition}.xlsx")


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

    production_sum_olefins = pd.read_excel(data_to_excel_path1, index_col=0, header=[0, 1])
    production_sum_ammonia = pd.read_excel(data_to_excel_path2, index_col=0, header=[0, 1])

    if include_prod_costs:
        df_costs = pd.read_excel(cost_data_excel, header=[0, 1], index_col=0)
        if 'costs_obj_interval' not in df_costs.index:
            raise KeyError("Row 'costs_obj_interval' not found in cost Excel")
        cost_values = df_costs.loc[['CAPEX', 'OPEX_fix', 'OPEX_var', 'OPEX_emis']]
    else:
        cost_values = None

    plt_obj = plot_production_shares(production_sum_olefins=production_sum_olefins,
                                     production_sum_ammonia=production_sum_ammonia,
                                     categories=categories,
                                     intervals=intervals,
                                     iterations=iterations,
                                     include_costs=include_prod_costs,
                                     cost_data=cost_values,
                                     total_cost=False,
                                     combined_categories=combined_categories)

    #saving options
    save = "both"
    if save == "pdf":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    elif save == "svg":
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
    elif save == "both":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')

    plt.show()

    # After all plots:
    # save_separate_legend(categories)



if __name__ == "__main__":
    main()



