import os
import numpy as np
import json
import matplotlib.pyplot as plt
import cmcrameri.cm as cmc  # pip install cmcrameri

# options
nr_iterations = 5
ambition = "Scope1-3"
location = "Zeeland"

# Define paths
basepath_results = f"Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/{ambition}"
result_file = os.path.join(
    basepath_results,
    "Results_model_linking_20250806_11_36",
    "epsilons.json"
)

tech_to_id = {
    "CrackerFurnace": "ICH01_01",
    "CrackerFurnace_bio": "ICH01_42",
    "CrackerFurnace_CC": "ICH01_02",
    "CrackerFurnace_CC_bio": "ICH01_03",
    "CrackerFurnace_Electric": "ICH01_05",
    "CrackerFurnace_Electric_bio": "ICH01_06",
    "SteamReformer": "Amm01_01",
    "SteamReformer_CC": "Amm01_02",
    "ElectricSMR_m": "Amm01_08",
    "AEC": "Amm01_05",
    "RWGS": "RFS03_02",
    "methanol_from_syngas": "RFS04_01",
    "MTO": "ICH01_12",
    "EDH": "ICH01_11",
    "PDH": "ICH01_41",
    "MPW2methanol_input": "WAI01_10",
    "MPW2methanol_input_CC": "WAI01_11",
    "Biomass2methanol_input": "RFS03_01",
    "Biomass2methanol_input_CC": "RFS03_05",
    "DirectMeOHsynthesis": "RFS04_02",
    "CO2electrolysis": "ICH01_40"
}

# --- Read JSON ---
with open(result_file, "r") as f:
    epsilons_data = json.load(f)

# Collect all tech IDs present in the JSON
all_tech_ids = sorted({
    tech_id
    for tech_dict in epsilons_data.values()
    for tech_id in tech_dict.keys()
})

# Assign colors to each tech ID from a Crameri colormap
cmap = cmc.batlow  # choose your Crameri palette
colors = {tech_id: cmap(i / max(1, len(all_tech_ids) - 1))
          for i, tech_id in enumerate(all_tech_ids)}

# Store values for average calculation
avg_epsilons = {}

plt.figure(figsize=(7, 5))

for tech_id in all_tech_ids:
    iter_list = []
    eps_list = []
    for iter_key, tech_dict in epsilons_data.items():
        iter_num = float(iter_key.split("_")[1])  # could be 3.5, 4.5 etc.
        if not iter_num.is_integer():  # skip fractional iterations
            continue
        iter_num = int(iter_num)
        if tech_id in tech_dict:
            for year, val in tech_dict[tech_id].items():
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    continue
                if np.isfinite(val):
                    iter_list.append(iter_num)
                    eps_list.append(val)
                    avg_epsilons.setdefault(iter_num, []).append(val)
    if iter_list:
        plt.scatter(
            iter_list,
            eps_list,
            label=tech_id,
            color=colors[tech_id],
            edgecolor="k",
            s=50
        )

# --- Plot average epsilon per iteration ---
avg_x = sorted(avg_epsilons.keys())
avg_y = [np.mean(avg_epsilons[i]) for i in avg_x]
plt.plot(avg_x, avg_y, "-o", color="black", lw=2, label="Average")

plt.xlabel("Iteration")
plt.ylabel("Epsilon")
plt.yscale("log")
plt.title(f"Epsilon values by technology ({ambition}, {location})")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.show()
