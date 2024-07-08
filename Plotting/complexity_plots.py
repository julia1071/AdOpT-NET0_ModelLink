import h5py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from matplotlib.ticker import PercentFormatter

from adopt_net0 import extract_datasets_from_h5group

# Define the data path
resultfolder = "Z:/PyHub/PyHub_results/CM_old/20240701_Chemelot_tests_complexity/BigM_Chemelot_cluster"
summarypath = Path(resultfolder) / 'Summary.xlsx'

# Extract the relevant data
summary_results = pd.read_excel(summarypath)

# full resolution reference
fullres_results = {
    'costs': summary_results[summary_results['case'] == 'fullres'].iloc[0]['total_npv'],
    'emissions': summary_results[summary_results['case'] == 'fullres'].iloc[0]['emissions_pos'],
    'computation time': summary_results[summary_results['case'] == 'fullres'].iloc[0]['time_total']
}
fullres_path_h5 = Path(summary_results[summary_results['case'] == 'fullres'].iloc[0]['time_stamp']) / "optimization_results.h5"

#get capacities from h5 files
if fullres_path_h5.exists():
    with h5py.File(fullres_path_h5, "r") as hdf_file:
        df = extract_datasets_from_h5group(hdf_file["design/nodes"])
        tecs = ['NaphthaCracker', 'NaphthaCracker_Electric']
        for tec in tecs:
            output_name = 'size_' + tec
            fullres_results[output_name] = df['period1', 'Chemelot', tec, 'size'].iloc[0]


#now collect data to plot
data = []
for case in summary_results['case']:
    if pd.notna(case) and case != 'fullres':
        case_data = {
            'case': case,
            'DD': int(case[2:]),
            'costs': summary_results.loc[summary_results['case'] == case, 'total_npv'].iloc[0],
            'emissions': summary_results.loc[summary_results['case'] == case, 'emissions_pos'].iloc[0],
            'computation time': summary_results.loc[summary_results['case'] == case, 'time_total'].iloc[0]
        }

        #collect sizes from h5
        case_path_h5 = Path(
            summary_results[summary_results['case'] == case].iloc[0]['time_stamp']) / "optimization_results.h5"

        if fullres_path_h5.exists():
            with h5py.File(fullres_path_h5, "r") as hdf_file:
                df = extract_datasets_from_h5group(hdf_file["design/nodes"])
                tecs = ['NaphthaCracker', 'NaphthaCracker_Electric']
                for tec in tecs:
                    output_name = 'size_' + tec
                    case_data[output_name] = df['period1', 'Chemelot', tec, 'size'].iloc[0]

        data.append(case_data)

# Convert the list of dictionaries into a DataFrame
clustered_results = pd.DataFrame(data)
clustered_results.set_index('case', inplace=True)

# difference
columns_of_interest = ['costs', 'emissions', 'computation time', 'size_NaphthaCracker']
for column in columns_of_interest:
    clustered_results[f'{column}_diff'] = ((clustered_results[column] - fullres_results[column]) / fullres_results[column]) * 100

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

# Define custom colors
# colors = ['#9fa0c3', '#8b687f', '#7b435b', '#4C4D71', '#B096A7']
colors = ['#639051', '#E4F0D0', '#5277B7', '#FFBC47']


# Create a new figure
fig, ax = plt.subplots(figsize=(5, 4))

# Scatter plots for differences
for i, column in enumerate(columns_of_interest):
    label = 'Size Naphtha Cracker' if column == 'size_NaphthaCracker' else f'{column.capitalize()}'
    ax.scatter(clustered_results['DD'], clustered_results[f'{column}_diff'], color=colors[i], label=label)

# Set labels and title
ax.set_xlabel('Number of Design Days')
ax.set_ylabel('Difference with Full Resolution')
ax.yaxis.set_major_formatter(PercentFormatter(decimals=1))

# Add grid and legend
ax.grid(True, alpha = 0.2)
ax.legend()


# Adjust layout
plt.tight_layout()


saveas = 'pdf'

if saveas == 'svg':
    savepath = 'C:/Users/5637635/Documents/OneDrive - Universiteit Utrecht/Images and graphs/Collection CM/Paper/' + 'complexity_minC.svg'
    plt.savefig(savepath, format='svg')
if saveas == 'pdf':
    savepath = 'C:/Users/5637635/Documents/OneDrive - Universiteit Utrecht/Images and graphs/Collection CM/Paper/' + 'complexity_minC.pdf'
    plt.savefig(savepath, format='pdf')

#show plot
# plt.show()
