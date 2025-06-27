import os
from pathlib import Path
import pandas as pd
import h5py
from adopt_net0 import extract_datasets_from_h5group

# --- Configuration ---
result_type = 'Brownfield'
result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
intervals = ["2030", "2040", "2050"]
location = "Zeeland"
output_path = "U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland/technology_sizes.xlsx"

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
            # --- Technology sizes ---
            nodedata = extract_datasets_from_h5group(hdf_file["design/nodes"])
            df_nodes = pd.DataFrame(nodedata)

            for tech in df_nodes.columns.levels[2]:
                col = (interval, location, tech, "size")
                value = df_nodes[col].iloc[0] if col in df_nodes.columns else 0
                row_label = f"size_{tech}"
                tech_sizes_df.loc[row_label, (result_type, location, interval)] = value

                # --- CC fraction for selected technologies ---
                if any(tech.startswith(base) for base in ["CrackerFurnace", "MPW2methanol", "SteamReformer"]):
                    opdata = extract_datasets_from_h5group(hdf_file["operation/technology_operation"])
                    opdata = {k: v for k, v in opdata.items() if len(v) >= 8670}
                    df_op = pd.DataFrame(opdata)

                    col_cc = (interval, location, tech, "CO2captured_output")
                    col_em = (interval, location, tech, "emissions_pos")

                    if col_cc in df_op.columns and col_em in df_op.columns:
                        numerator = df_op[col_cc].sum()
                        print(numerator)
                        denominator = numerator + df_op[col_em].sum()
                        print(denominator)
                        frac_CC = numerator / denominator if (denominator > 1 and numerator > 1) else 0

                        row_label_cc = f"size_{tech}_CC"
                        tech_sizes_df.loc[row_label_cc, (result_type, location, interval)] = frac_CC

# Save to Excel
tech_sizes_df.to_excel(output_path)
print("Saved technology sizes to:", output_path)
