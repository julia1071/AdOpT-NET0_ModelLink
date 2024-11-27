import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.lines import Line2D
from cmcrameri import cm

# Define the data path
datapath = "Z:/AdOpt_NET0/AdOpt_data/MY/241119_MY_Data_Chemelot"
el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_MY.xlsx'

# Years to plot and their colors
node = 'Zeeland'
years = ['2030', '2040', '2050']
labels = {'2030': 'Short-term', '2040': 'Mid-term', '2050': 'Long-term'}
# colors = {'2030': '#93ABC7', '2040': '#4D5382', '2050': '#3B3348'}
colors = cm.lipari(np.linspace(0, 0.8, len(years)))

# Dictionary to store data
data = {}

# Load data for each year
for year in years:
    el_importdata = pd.read_excel(el_load_path, sheet_name=year, header=0, nrows=8760)
    if node == 'Chemelot':
        data[year] = {
            'price': el_importdata.iloc[:, 0],
            'emission': el_importdata.iloc[:, 2]
        }
    elif node == 'Zeeland':
        data[year] = {
            'price': el_importdata.iloc[:, 1],
            'emission': el_importdata.iloc[:, 2]
        }

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

# Create a figure with a 3x2 grid layout, adjusting width to page and reducing height and whitespace
fig = plt.figure(figsize=(7, 7))  # Adjust width (7 inches for standard page) and height (6 inches)
gs = fig.add_gridspec(3, 2, height_ratios=[1.5, 1.5, 0.8], width_ratios=[1, 1])
fig.subplots_adjust(hspace=0.3, wspace=0.25, top=0.95, bottom=0.1, left=0.1, right=0.98)  # Reduce whitespace

# Create custom legend handles with thicker lines
custom_lines = [Line2D([0], [0], color=colors[i], linewidth=2) for i in range(len(years))]

# First row: line plots for prices and emissions
ax_price = fig.add_subplot(gs[0, :])
ax_emission = fig.add_subplot(gs[1, :], sharex=ax_price)

# Plot electricity prices
for i, year in enumerate(years):
    ax_price.plot(data[year]['price'], color=colors[i], label=f'Price {labels[year]}', linewidth=0.5)
ax_price.set_ylabel('Electricity Price [EUR/MWh]')
ax_price.set_xlim(0, 8759)
ax_price.set_ylim(0, 200)
ax_price.legend(custom_lines, [labels[year] for year in years], loc='upper right', ncol=1)

# Add a zoomed-in inset for hours 2200-2500 in the price plot
ax_inset = inset_axes(ax_price, width="15%", height="30%", bbox_to_anchor=(-0.5, 0, 1, 1), bbox_transform=ax_price.transAxes)
for i, year in enumerate(years):
    ax_inset.plot(data[year]['price'], color=colors[i], linewidth=0.5)
ax_inset.set_xlim(2350, 2400)
ax_inset.set_ylim(0, 10000)
ax_inset.tick_params(labelsize=8)  # Smaller tick labels for the inset


# Plot emission rates
for i, year in enumerate(years):
    ax_emission.plot(data[year]['emission'], color=colors[i], linestyle='--', label=f'Emissions {labels[year]}', linewidth=0.5)
ax_emission.set_xlabel('Time (hours)')
ax_emission.set_ylabel('Emission Rate [t CO$_2$/MWh]')
ax_emission.set_ylim(0, 0.3)
ax_emission.legend(custom_lines, [labels[year] for year in years], loc='upper right', ncol=1)

# Third row: histograms for price and emission
ax_hist1 = fig.add_subplot(gs[2, 0])
ax_hist2 = fig.add_subplot(gs[2, 1])

# Plot the ECDF for electricity prices
for i, year in enumerate(years):
    ecdf_price = pd.Series(data[year]['price']).value_counts(normalize=True).sort_index().cumsum()
    ax_hist1.plot(ecdf_price.index, 1 - ecdf_price.values, color=colors[i], label=labels[year], linewidth=0.8)
ax_hist1.set_xlabel('Electricity Price [EUR/MWh]')
ax_hist1.set_ylabel('Probability')
ax_hist1.set_xlim(0, 200)  # Manually set the x-axis limit for electricity prices
ax_hist1.legend(custom_lines, [labels[year] for year in years], loc='upper right', ncol=1)

# Plot the ECDF for emissions
for i, year in enumerate(years):
    ecdf_emission = pd.Series(data[year]['emission']).value_counts(normalize=True).sort_index().cumsum()
    ax_hist2.plot(ecdf_emission.index, 1 - ecdf_emission.values, color=colors[i], linestyle='--', label=labels[year], linewidth=0.8)
ax_hist2.set_xlabel('Emission Rate [t CO$_2$/MWh]')
ax_hist2.set_ylabel('Probability')
ax_hist2.legend(custom_lines, [labels[year] for year in years], loc='upper right', ncol=1)



# Save the plot
saveas = 'pdf'
savepath = 'C:/Users/5637635/Documents/OneDrive - Universiteit Utrecht/Research/Multiyear Modeling/MY_Plots/'
plt.savefig(f"{savepath}Fig_eprice_cum_{node}.{saveas}", format=saveas)

# Show plot
plt.show()
