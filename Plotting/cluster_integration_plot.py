import os

import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import PercentFormatter
from adopt_net0 import extract_datasets_from_h5group

# Define the data path
resultfolder = "Z:/PyHub/PyHub_results/CM/Cluster_integration"
data_to_excel_path = 'C:/EHubversions/AdOpT-NET0_Julia/Plotting/result_data.xlsx'

get_data = 0

if get_data == 1:
    # Define the multi-level index for rows
    columns = pd.MultiIndex.from_product(
        [
            ["Chemelot", "Zeeland"],
            ["cluster", "ethylene", "ammonia", "standalone"],
            ["minC_ref", "minC_high", "minE"]
        ],
        names=["Location", "Type", "Scenario"]
    )

    # Define the columns
    index = ["path", "costs_tot", "emissions_tot", 'size_NaphthaCracker', 'size_NaphthaCracker_Electric',
             'size_NaphthaCracker_CC', 'size_KBRreformer', 'size_KBRreformer_CC', 'size_eSMR', 'size_AEC',
             'costs_spec', 'costs_spec_cor']

    # Create the DataFrame with NaN values
    result_data = pd.DataFrame(np.nan, index=index, columns=columns)

    lev0 = ['Chemelot', 'Zeeland']

    # Fill the path column using a loop
    for location in lev0:
        for typ in result_data.columns.levels[1]:
            if typ != 'standalone':
                folder_name = f"{location}_{typ}"
                summarypath = os.path.join(resultfolder, folder_name, "Summary.xlsx")
                summary_results = pd.read_excel(summarypath)

                for scenario in result_data.columns.levels[2]:
                    for case in summary_results['case']:
                        if pd.notna(case) and scenario in case:
                            h5_path = Path(summary_results[summary_results['case'] == case].iloc[0]['time_stamp']) / "optimization_results.h5"
                            result_data.loc["path", (location, typ, scenario)] = h5_path
                            result_data.loc["costs_tot", (location, typ, scenario)] = summary_results[summary_results['case'] == case].iloc[0]['total_npv']
                            result_data.loc["emissions_tot", (location, typ, scenario)] = summary_results[summary_results['case'] == case].iloc[0]['emissions_pos']

                            if h5_path.exists():
                                with h5py.File(h5_path, "r") as hdf_file:
                                    df = extract_datasets_from_h5group(hdf_file["design/nodes"])
                                    tecs = ['NaphthaCracker', 'NaphthaCracker_Electric', 'NaphthaCracker_CC', 'KBRreformer', 'KBRreformer_CC', 'eSMR', 'AEC']
                                    for tec in tecs:
                                        output_name = 'size_' + tec
                                        if ('period1', 'Chemelot', tec, 'size') in df.columns:
                                            result_data.loc[output_name, (location, typ, scenario)] = df[('period1', 'Chemelot', tec, 'size')].iloc[0]
                                        else:
                                            result_data.loc[output_name, (location, typ, scenario)] = 0


    # calculate total product
    products = {
        "Chemelot": {
            "ammonia": 135 * 8760,
            "ethylene": 150 * 8760,
            "cracker_tot": None,
            "total_product": None,
            "total_product_cor": None
        },
        "Zeeland": {
                "ammonia": 208 * 8760,
                "ethylene": 208 * 8760,
                "cracker_tot": None,
                "total_product": None,
                "total_product_cor": None
        }
    }

    ethylene_yield = 0.3025

    for location in products:
        products[location]['total_product'] = products[location]['ammonia'] + products[location]['ethylene']
        products[location]['cracker_tot'] = products[location]['ethylene'] / ethylene_yield
        products[location]['total_product_cor'] = products[location]['ammonia'] + products[location]['cracker_tot']



    # Make calculations with results
    for location in result_data.columns.levels[0]:
        for scenario in result_data.columns.levels[2]:
            for row in result_data.index:
                if row != 'path':
                    result_data.loc[row, (location, 'standalone', scenario)] = result_data.loc[row, (
                    location, 'ethylene', scenario)] + result_data.loc[row, (location, 'ammonia', scenario)]
                else:
                    result_data.loc[row, (location, 'standalone', scenario)] = None

            # get specific costs and emissions
            result_data.loc['costs_spec', (location, 'cluster', scenario)] = result_data.loc['costs_tot', (
                location, 'cluster', scenario)] / products[location]['total_product']
            result_data.loc['costs_spec_cor', (location, 'cluster', scenario)] = result_data.loc['costs_tot', (
                location, 'cluster', scenario)] / products[location]['total_product_cor']
            result_data.loc['emissions_spec', (location, 'cluster', scenario)] = result_data.loc['emissions_tot', (
                location, 'cluster', scenario)] / products[location]['total_product']
            result_data.loc['emissions_spec_cor', (location, 'cluster', scenario)] = result_data.loc['emissions_tot', (
                location, 'cluster', scenario)] / products[location]['total_product_cor']

            result_data.loc['costs_spec', (location, 'ethylene', scenario)] = result_data.loc['costs_tot', (
                location, 'ethylene', scenario)] / products[location]['ethylene']
            result_data.loc['costs_spec_cor', (location, 'ethylene', scenario)] = result_data.loc['costs_tot', (
                location, 'ethylene', scenario)] / products[location]['cracker_tot']
            result_data.loc['emissions_spec', (location, 'ethylene', scenario)] = result_data.loc['emissions_tot', (
                location, 'ethylene', scenario)] / products[location]['ethylene']
            result_data.loc['emissions_spec_cor', (location, 'ethylene', scenario)] = result_data.loc['emissions_tot', (
                location, 'ethylene', scenario)] / products[location]['cracker_tot']

            result_data.loc['costs_spec', (location, 'ammonia', scenario)] = result_data.loc['costs_tot', (
                location, 'ammonia', scenario)] / products[location]['ammonia']
            result_data.loc['emissions_spec', (location, 'ammonia', scenario)] = result_data.loc['emissions_tot', (
                location, 'ammonia', scenario)] / products[location]['ammonia']

            result_data.loc['costs_spec', (location, 'standalone', scenario)] = result_data.loc['costs_tot', (
                location, 'standalone', scenario)] / products[location]['total_product']
            result_data.loc['costs_spec_cor', (location, 'standalone', scenario)] = result_data.loc['costs_tot', (
                location, 'standalone', scenario)] / products[location]['total_product_cor']
            result_data.loc['emissions_spec', (location, 'standalone', scenario)] = result_data.loc['emissions_tot', (
                location, 'standalone', scenario)] / products[location]['total_product']
            result_data.loc['emissions_spec_cor', (location, 'standalone', scenario)] = result_data.loc['emissions_tot', (
                location, 'standalone', scenario)] / products[location]['total_product_cor']

    result_data.to_excel(data_to_excel_path)

if get_data == 0:
    result_data = pd.read_excel(data_to_excel_path, index_col=0, header=[0, 1, 2])

# Configure Matplotlib to use LaTeX for text rendering and set font
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 12,
    "font.size": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


#Select data to plot (ethylene will be standalone later)
locations = ['Chemelot', 'Zeeland']
types = ['cluster', 'standalone']
scenarios = ['minC_ref', 'minC_high']
metric = 'costs_spec'

# Extract the relevant data from the DataFrame and prepare data
plot_data = result_data.loc[metric, locations[0]]
plot_data = plot_data.loc[types, scenarios]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))

# Define custom colors and layout
colors = ['#F1DAC4', '#474973']
bar_width = 0.15
n_types = len(types)
n_scenarios = len(scenarios)
n_locations = len(locations)
total_bars = n_types * n_scenarios

# Set positions of the bars
index = np.arange(n_locations) * (total_bars + 1) * bar_width

# Create custom patches for the legend
legend_elements = [
    plt.Line2D([0], [0], color=colors[0], lw=4, alpha=0.5, label='cluster (reference CO$_2$ tax)'),
    plt.Line2D([0], [0], color=colors[0], lw=4, label='cluster (high CO$_2$ tax)'),
    plt.Line2D([0], [0], color=colors[1], lw=4, alpha=0.5, label='standalone (reference CO$_2$ tax)'),
    plt.Line2D([0], [0], color=colors[1], lw=4,  label='standalone (high CO$_2$ tax)')
]

# Plot each location
for loc_idx, location in enumerate(locations):
    plot_data = result_data.loc[metric, location].loc[types, scenarios]

    # Plot each scenario for each type
    for j, scenario in enumerate(scenarios):
        for i, typ in enumerate(types):
            position = index[loc_idx] + (i * n_scenarios + j) * bar_width
            if scenario == 'minC_ref':
                plt.bar(position, plot_data.loc[typ, scenario], bar_width,
                        label=None, color=colors[i], alpha=0.5)
            elif scenario == 'minC_high':
                plt.bar(position, plot_data.loc[typ, scenario], bar_width,
                        label=None, color=colors[i])

# Adding labels and title
plt.ylabel('Specific costs [€/tonne product]')
plt.xticks(index + bar_width * (total_bars - 1) / 2, locations)
plt.legend(handles=legend_elements, loc='upper right')

# Adjust layout
plt.tight_layout()


saveas = '0'

if saveas == 'svg':
    savepath = 'C:/Users/5637635/Documents/OneDrive - Universiteit Utrecht/Images and graphs/Collection CM/Paper/' + 'integration_costs.svg'
    plt.savefig(savepath, format='svg')
if saveas == 'pdf':
    savepath = 'C:/Users/5637635/Documents/OneDrive - Universiteit Utrecht/Images and graphs/Collection CM/Paper/' + 'integration_costs.pdf'
    plt.savefig(savepath, format='pdf')

#show plot
plt.show()
