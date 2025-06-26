
import h5py
import pandas as pd
from pathlib import Path
from adopt_net0 import extract_datasets_from_h5group

# result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
# intervals =['2030','2040','2050']
# location = "Zeeland"


def extract_cc_fractions(result_folder, intervals, location, cc_technologies):
    """
    Extracts carbon capture (CC) fractions for specified technologies from HDF5 result files
    in the cluster model output.

    Args:
        result_folder (Path): Path to the folder containing the optimization results and Summary.xlsx
        intervals (list): List of year intervals to extract CC fractions for
        location (str): The location identifier used in the result columns
        cc_technologies (list): List of base technology name prefixes to include in the CC fraction analysis

    Returns:
        dict: Dictionary with keys (location, interval, technology) and values as CC fractions (floats between 0 and 1)
    """
    print("Extracting CC fractions of technologies in the cluster model")

    summary_path = result_folder/ "Summary.xlsx"
    try:
        summary_df = pd.read_excel(summary_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing summary: {summary_path}")

    cc_fraction_dict = {}

    for _, row in summary_df.iterrows():
        case = row["case"]
        if pd.isna(case):
            continue

        for interval in intervals:
            if interval not in case:
                continue

            h5_path = Path(result_folder) / row["time_stamp"] / "optimization_results.h5"
            if not h5_path.exists():
                print(f"Missing h5 file: {h5_path}")
                continue

            with h5py.File(h5_path, "r") as hdf_file:
                df_nodes = pd.DataFrame(extract_datasets_from_h5group(hdf_file["design/nodes"]))
                opdata = extract_datasets_from_h5group(hdf_file["operation/technology_operation"])
                opdata = {k: v for k, v in opdata.items() if len(v) >= 8670}
                df_op = pd.DataFrame(opdata)

                if df_nodes.columns.nlevels > 2:
                    for tech in df_nodes.columns.levels[2]:
                        if any(tech.startswith(base) for base in cc_technologies):
                            col_cc = (interval, location, tech, "CO2captured_output")
                            col_em = (interval, location, tech, "emissions_pos")

                            if col_cc in df_op.columns and col_em in df_op.columns:
                                numerator = df_op[col_cc].sum()
                                denominator = numerator + df_op[col_em].sum()
                                frac_CC = numerator / denominator if (denominator > 1 and numerator > 1) else 0
                                cc_fraction_dict[(location, interval, tech)] = float(frac_CC)
    return cc_fraction_dict

# extract_cc_fractions(result_folder, intervals, location)