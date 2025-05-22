import os
from pathlib import Path
import pandas as pd
import h5py
from adopt_net0 import extract_datasets_from_h5group

# --- Configuration ---
result_type = 'EmissionLimit_Brownfield'
result_folder = Path("U:/Data AdOpt-NET0/Test/Result path/EL_Chemelot")
intervals = ["2030", "2040", "2050"]
location = "Chemelot"

# --- Main Process ---
summary_path = result_folder / "Summary.xlsx"
try:
    summary_df = pd.read_excel(summary_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing summary: {summary_path}")

# Dictionary to store sizes in the form {(location, interval, tech): value}
tech_size_dict = {}

for _, row in summary_df.iterrows():
    case = row["case"]
    if pd.isna(case):
        continue

    for interval in intervals:
        if interval not in case:
            continue

        h5_path = result_folder / row["time_stamp"] / "optimization_results.h5"
        if not h5_path.exists():
            print(f"Missing h5 file: {h5_path}")
            continue

        with h5py.File(h5_path, "r") as hdf_file:
            nodedata = extract_datasets_from_h5group(hdf_file["design/nodes"])
            df_nodes = pd.DataFrame(nodedata)

            all_techs = df_nodes.columns.levels[2] if df_nodes.columns.nlevels > 2 else []
            for tech in all_techs:
                col = (interval, location, tech, "size")
                value = df_nodes[col].iloc[0] if col in df_nodes.columns else 0
                tech_size_dict[(location, interval, tech)] = value

# Print resulting dictionary (optional)
for key, value in tech_size_dict.items():
    print(f"{key}: {value}")

value = tech_size_dict.get(("Chemelot", "2040", "AEC"))
print(value)