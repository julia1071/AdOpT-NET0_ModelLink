import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

# Define the data path
datapath = "Z:/PyHub/PyHub_data/CM/100624_CM"
el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_CM.csv'

# Read the CSV file
el_importdata = pd.read_csv(el_load_path, sep=';', header=0, nrows=8760)

# Extract the relevant data
el_price = el_importdata.iloc[:, 0]
el_price2 = el_importdata.iloc[:, 1]
el_emissionrate = el_importdata.iloc[:, 3]

# Define the custom colors
color_price = (71/255, 73/255, 115/255)  # Color for the first electricity price
color_price2 = (166/255, 156/255, 172/255)  # Color for the second electricity price
color_emission = (161/255, 192/255, 132/255)  # Color for the emission rate

# Create a new figure and axis
fig, ax1 = plt.subplots(figsize=(12, 3))

# Plot the first line on the left y-axis with the custom color
ax1.plot(el_price, color=color_price, label='Chemelot', linewidth=0.5)
ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Electricity Price [EUR/MWh]')
ax1.tick_params(axis='y')
ax1.set_xlim(0, 8759)

# Plot the second line on the left y-axis with the second custom color
ax1.plot(el_price2, color=color_price2, label='Zeeland', linewidth=0.5)

# Create a second y-axis for the emissions
ax2 = ax1.twinx()
ax2.plot(el_emissionrate, color=color_emission, linestyle='--', label='Grid emissions',linewidth=0.5)
ax2.set_ylabel('Emission Rate [t CO_2/MWh]', color=color_emission)
ax2.tick_params(axis='y', labelcolor=color_emission)

# # Create zoom inset
# axins = zoomed_inset_axes(ax1, 4, loc='upper center')  # zoom = 2
# axins.plot(el_price, color=color_price, linewidth=0.8)
# axins.plot(el_price2, color=color_price2, linewidth=0.8)
# # axins.plot(el_emissionrate, color=color_emission, linestyle='--', linewidth=0.8)
# x1, x2 = 2400, 2640 # specify the limits
# axins.set_xlim(x1, x2)
# axins.set_ylim(30, 130)
# plt.xticks(visible=False)
# plt.yticks(visible=False)
# mark_inset(ax1, axins, loc1=2, loc2=4, fc="none", ec="0.5")

# Add a legend
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

# Use LaTeX for subscript in axis labels
plt.rcParams['text.usetex'] = True
ax1.set_ylabel(r'Electricity Price [EUR/MWh]', fontsize=12)
ax1.set_xlabel(r'Time (hours)', fontsize=12)
ax2.set_ylabel(r'Emission Rate [t CO$_2$/MWh]', fontsize=12)

# Show the plot
# plt.title('Electricity Price and Emission Rate')
plt.show()