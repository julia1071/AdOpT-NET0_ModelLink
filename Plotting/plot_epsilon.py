import os
import numpy as np
import json
import matplotlib.pyplot as plt
import cmcrameri.cm as cmc  # pip install cmcrameri

plt.rcParams.update({
    'font.size': 14,              # base font size
    'font.family': 'serif',       # use serif fonts
})

# Options
nr_iterations = 3
ambition = "Scope1-2"
location = "Zeeland"
save = "both"  # options: "pdf", "svg", "both", "no"

# Define paths
basepath_results = f"Z:/AdOpt_NET0/AdOpt_results/Model_Linking/Full/{ambition}"
result_file = os.path.join(
    basepath_results,
    "Results_model_linking_20250906_11_16",
    "epsilons.json"
)
plot_folder = os.path.join(
    "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python",
    f"Epsilons_{ambition}"
)

# Technology name to ID mapping
tech_to_id = {
    "CrackerFurnace": "ICH01_01",
    "CrackerFurnace_bio": "ICH01_42",
    "CrackerFurnace with CC": "ICH01_02",
    "CrackerFurnace with CC and bio": "ICH01_03",
    "Electric Cracker": "ICH01_05",
    "Electric Cracker with bio": "ICH01_06",
    "Steam Reformer": "Amm01_01",
    "Steam Reformer with CC": "Amm01_02",
    "Electric SMR ammonia": "Amm01_08",
    "Electric SMR ethylene": "RFS03_04",
    "AEC": "Amm01_05",
    "reverse WGS": "RFS03_02",
    "MeOH from syngas": "RFS04_01",
    "MTO": "ICH01_12",
    "EDH": "ICH01_11",
    "PDH": "ICH01_41",
    "MPW gasification": "WAI01_10",
    "MPW gasification with CC": "WAI01_11",
    "Biomass gasification input": "RFS03_01",
    "Biomass gasification with CC": "RFS03_05",
    "Direct MeOH synthesis": "RFS04_02",
    "CO$_2$ electrolysis": "ICH01_40"
}

# Reverse mapping: ID → Name
id_to_tech = {v: k for k, v in tech_to_id.items()}

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
cmap = cmc.batlow
colors = {tech_id: cmap(i / max(1, len(all_tech_ids) - 1))
          for i, tech_id in enumerate(all_tech_ids)}

# Store values for average calculation
avg_epsilons = {}

plt.rcParams.update({'font.family': 'serif'})
plt.figure(figsize=(9, 5))

for tech_id in all_tech_ids:
    iter_list = []
    eps_list = []
    for iter_key, tech_dict in epsilons_data.items():
        iter_num = float(iter_key.split("_")[1])
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
            label=id_to_tech.get(tech_id, tech_id),  # show tech name if available
            color=colors[tech_id],
            edgecolor="k",
            s=50
        )

# --- Plot average epsilon per iteration ---
avg_x = sorted(avg_epsilons.keys())
avg_y = [np.mean(avg_epsilons[i]) for i in avg_x]
plt.plot(avg_x, avg_y, "-o", color="black", lw=2, label="Average")

# X-axis as Iteration labels
plt.xticks(avg_x, [f"Iteration {i}" for i in avg_x])

# plt.xlabel("Iteration")
plt.ylabel("Epsilon")
# plt.ylim(-0.25, 1.25)
plt.yscale("log")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=12)
plt.tight_layout()

# --- Save plot ---
if save == "pdf":
    plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
elif save == "svg":
    plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
elif save == "both":
    plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')

plt.show()
