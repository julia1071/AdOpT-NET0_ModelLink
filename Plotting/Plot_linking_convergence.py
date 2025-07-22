import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

#Settings
inputs = 0

# Define the path to the JSON file
basepath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/"
if inputs:
    results_path = basepath + "Results_model_linking_20250718_17_15/inputs_cluster.json"
else:
    results_path = basepath + "Results_model_linking_20250718_17_15/outputs_cluster.json"

# Load the JSON data
with open(results_path, "r") as f:
    data = json.load(f)

# Extract all iterations
iterations = sorted(data.keys(), key=lambda x: int(x.split("_")[1]))

# Assume one region (e.g., "Zeeland")
region = next(iter(data[iterations[0]].keys()))

# Extract all years and parameters
years = sorted(data[iterations[0]][region].keys())
parameters = list(data[iterations[0]][region][years[0]].keys())

# Initialize trajectories: {param: {year: [values over iterations]}}
trajectories = {param: {year: [] for year in years} for param in parameters}

# Fill in values
for iteration in iterations:
    for year in years:
        for param in parameters:
            value = data[iteration][region][year][param]
            trajectories[param][year].append(value)

# Filter parameters where **all** values are None
def has_valid_data(param_data):
    for year_data in param_data.values():
        if any(v is not None for v in year_data):
            return True
    return False

valid_params = [param for param in parameters if has_valid_data(trajectories[param])]

# Set up subplots
num_valid = len(valid_params)
fig, axs = plt.subplots(nrows=(num_valid + 1) // 2, ncols=2, figsize=(12, 3.5 * ((num_valid + 1) // 2)))
axs = axs.flatten()

# For collecting legend handles/labels
legend_handles = []
legend_labels = []

# Plot each valid parameter
for i, param in enumerate(valid_params):
    ax = axs[i]
    for year in years:
        values = trajectories[param][year]
        if all(v is None for v in values):
            continue  # skip if no data for this year
        line, = ax.plot(range(1, len(values) + 1), values, marker='o', label=year)
        if year not in legend_labels:
            legend_handles.append(line)
            legend_labels.append(year)
    ax.set_title(f"Convergence of {param}")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # only integer ticks
    ax.grid(True)

# Hide unused subplots
for j in range(len(valid_params), len(axs)):
    fig.delaxes(axs[j])

# One global legend
fig.legend(legend_handles, legend_labels, loc='upper center', ncol=len(years), bbox_to_anchor=(0.5, 1.05))

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.90, hspace=0.4, wspace=0.3)
plt.show()
