from pathlib import Path
import pandas as pd
import h5py
from adopt_net0 import extract_datasets_from_h5group
from conversion_factors import conversion_factor_cluster_to_IESA

# --- Configuration ---
result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
intervals = ["2030", "2040", "2050"]
location = "Zeeland"

def extract_data_cluster(result_folder, intervals, location):

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

                if df_nodes.columns.nlevels > 2:
                    all_techs = df_nodes.columns.levels[2]
                    for tech in all_techs:
                        for interval in intervals:
                            col = (interval, location, tech, "size")
                            value = df_nodes[col].iloc[0] if col in df_nodes.columns else 0
                            tech_size_dict[(location, interval, tech)] = float(value)

    return tech_size_dict


print(extract_data_cluster(result_folder, intervals, location))