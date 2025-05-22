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
output_path = "U:/Data AdOpt-NET0/Test/Result path/EL_Chemelot/technology_sizes.xlsx"

# --- Main Process ---
summary_path = result_folder / "Summary.xlsx"
try:
    summary_df = pd.read_excel(summary_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing summary: {summary_path}")

# Define MultiIndex columns for output DataFrame
columns = pd.MultiIndex.from_product(
    [[str(result_type)], [location], intervals],
    names=["Resulttype", "Location", "Interval"]
)
tech_sizes_df = pd.DataFrame(columns=columns)

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

            for tech in df_nodes.columns.levels[2]:
                col = (interval, location, tech, "size")
                value = df_nodes[col].iloc[0] if col in df_nodes.columns else 0
                row_label = f"size_{tech}"
                tech_sizes_df.loc[row_label, (result_type, location, interval)] = value

# Save to Excel
tech_sizes_df.to_excel(output_path)
print("Saved technology sizes to:", output_path)