import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cmcrameri.cm as cmc


# Global style settings
plt.rcParams.update({
    'font.size': 14,              # base font size
    'font.family': 'serif',       # use serif fonts
})

def plot_costs_bar(ambitions, datapath, total_cost=False, include_emissions=True):
    """
    Plots a grouped bar chart of costs for ambition levels using the 'lapaz' color scheme.
    Optionally overlays emissions/tonne product as dots on a secondary y-axis.
    """
    # Store results
    cost_dict = {}
    emissions_dict = {}

    for ambition in ambitions:
        fpath = os.path.join(datapath, "Plotting", "Results_excels", f"result_data_long_{ambition}.xlsx")
        df = pd.read_excel(fpath, header=[0, 1], index_col=0)

        # Costs
        if 'costs_obj_interval' not in df.index:
            raise KeyError(f"Row 'costs_obj_interval' not found in file: {fpath}")
        costs = df.loc['costs_obj_interval']
        if not total_cost:
            costs = costs / 2_901_310
        if isinstance(costs.index, pd.MultiIndex):
            costs.index = [' '.join(map(str, idx)).strip() for idx in costs.index]
        cost_dict[ambition] = costs.values

        # Emissions
        if include_emissions:
            if 'emissions_net' not in df.index:
                raise KeyError(f"Row 'emissions_net' not found in file: {fpath}")
            emissions = df.loc['emissions_net']
            if not total_cost:
                emissions = emissions / 2_901_310
            if isinstance(emissions.index, pd.MultiIndex):
                emissions.index = [' '.join(map(str, idx)).strip() for idx in emissions.index]
            emissions_dict[ambition] = emissions.values

    # Convert to DataFrames
    df_costs = pd.DataFrame(cost_dict, index=costs.index)
    df_emissions = pd.DataFrame(emissions_dict, index=costs.index) if include_emissions else None

    # Plot setup
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(df_costs.index))
    bar_width = 0.8 / len(ambitions)

    # Colors from Crameri 'lapaz'
    cmap = cmc.lapaz
    colors = cmap(np.linspace(0.1, 0.85, len(ambitions)))

    # Bars
    for i, ambition in enumerate(ambitions):
        ax.bar(x + i * bar_width, df_costs[ambition], width=bar_width,
               label=ambition, color=colors[i])

    # Secondary axis for emissions (no legend entry)
    if include_emissions and df_emissions is not None:
        ax2 = ax.twinx()
        for i, ambition in enumerate(ambitions):
            ax2.plot(x + i * bar_width, df_emissions[ambition], 'o',
                     color=cmap(0), markersize=6, label="_nolegend_")  # hides from legend
        ax2.set_ylabel("Emissions [tCO$_2$/t product]")
        ax2.tick_params(axis='y')

    # Labels & legend
    ylabel = "Costs [€/t product]" if not total_cost else "Total costs [€]"
    ax.set_ylabel(ylabel)
    ax.set_xticks(x + bar_width * (len(ambitions)-1) / 2)
    ax.set_xticklabels(['2030', '2040', '2050'])
    ax.grid(False)

    # Merge legends from both axes if emissions are plotted
    if include_emissions and df_emissions is not None:
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(handles1 + handles2, labels1 + labels2, loc='best')
    else:
        ax.legend()

    plt.tight_layout()
    return fig, ax


def main():
    flag_cluster_ambition = ["Scope1-3", "Scope1-2", "LowAmbition"]
    total_cost = False
    include_emissions = False

    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plot_folder = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/ProdCosts_Standalone"

    fig, ax = plot_costs_bar(flag_cluster_ambition, datapath, total_cost=total_cost, include_emissions=include_emissions)

    save = "both"
    if save == "pdf":
        fig.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    elif save == "svg":
        fig.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
    elif save == "both":
        fig.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
        fig.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')

    plt.show()


if __name__ == "__main__":
    main()

