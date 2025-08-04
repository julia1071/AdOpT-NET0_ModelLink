import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import Model_linking.config_model_linking as cfg

# Settings
inputs = 1  # 1 for inputs_cluster.json, 0 for outputs_cluster.json
ambition = "Scope1-3"

# Tech ID to name mapping (reverse of your dict)
tech_to_id = cfg.tech_to_id

# Reverse mapping: tech_id → tech_name
id_to_tech = {v: k for k, v in tech_to_id.items()}

# Define the path to the JSON file
basepath = "Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/" + ambition
if inputs:
    results_path = basepath + "/Results_model_linking_20250803_19_05/inputs_cluster.json"
else:
    results_path = basepath + "/Results_model_linking_20250803_19_05/outputs_cluster.json"

# Load JSON data
with open(results_path, "r") as f:
    data = json.load(f)

# Extract all iterations sorted by iteration number
iterations = sorted(data.keys(), key=lambda x: int(x.split("_")[1]))

# Detect structure with region
first_iter = data[iterations[0]]
first_key = next(iter(first_iter))
has_region = isinstance(first_iter[first_key], dict) and any(
    isinstance(v, dict) for v in first_iter[first_key].values()
)

if has_region:
    # inputs_cluster.json structure (with region)
    region = next(iter(first_iter.keys()))
    years = sorted(first_iter[region].keys())
    parameters = list(first_iter[region][years[0]].keys())
    trajectories = {param: {year: [] for year in years} for param in parameters}

    for iteration in iterations:
        for year in years:
            for param in parameters:
                value = data[iteration][region][year].get(param, None)
                trajectories[param][year].append(value)

else:
    # outputs_cluster.json structure (no region)
    years = set()
    parameters = set()
    for iteration in iterations:
        for param, year_values in data[iteration].items():
            parameters.add(param)
            if isinstance(year_values, dict):
                years.update(year_values.keys())

    years = sorted(years)
    parameters = sorted(parameters)

    # Map tech IDs to names if possible
    mapped_parameters = []
    for param in parameters:
        mapped_parameters.append(id_to_tech.get(param, param))  # fallback to original if no mapping

    # Initialize trajectories with mapped param names
    trajectories = {param_name: {year: [] for year in years} for param_name in mapped_parameters}

    for iteration in iterations:
        for param in parameters:
            year_values = data[iteration].get(param, {})
            mapped_param = id_to_tech.get(param, param)
            for year in years:
                value = year_values.get(year, None)
                trajectories[mapped_param][year].append(value)

    parameters = mapped_parameters  # overwrite parameters with names

# Filter out parameters where all values are None
def has_valid_data(param_data):
    for year_data in param_data.values():
        if any(v is not None for v in year_data):
            return True
    return False

valid_params = [param for param in parameters if has_valid_data(trajectories[param])]

# Set up figure size - only increase vertical size for outputs
if inputs:
    figsize = (12, 3.5 * ((len(valid_params) + 1) // 2))
else:
    figsize = (12, 4.5 * ((len(valid_params) + 1) // 2))  # wider vertically for outputs

fig, axs = plt.subplots(nrows=(len(valid_params) + 1) // 2, ncols=2, figsize=figsize)
axs = axs.flatten()

# (plotting loop here...)

# Hide unused subplots
for j in range(len(valid_params), len(axs)):
    fig.delaxes(axs[j])

legend_handles = []
legend_labels = []

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
    # ax.set_xlabel("Iteration")
    if inputs:
        ax.set_ylabel("Price")
    else:
        ax.set_ylabel("Minimum use")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True)

# Add one global legend on top, centered
fig.legend(legend_handles, legend_labels, loc='upper center', ncol=len(years), bbox_to_anchor=(0.5, 1))

# Adjust layout to fit legend and plots well
plt.tight_layout()
plt.subplots_adjust(top=0.88, hspace=0.4, wspace=0.3)  # Leave space for legend above

plt.show()
