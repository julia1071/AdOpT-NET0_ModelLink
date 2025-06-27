
import h5py
import pandas as pd
from pathlib import Path
from adopt_net0 import extract_datasets_from_h5group

result_folder = Path(r"U:\Data AdOpt-NET0\Model_Linking_simplified\Results\Zeeland\Results_model_linking_20250626_18_54\Iteration_1")
intervals =['2030','2040','2050']
location = "Zeeland"

cc_technologies = {
    "CrackerFurnace": "CrackerFurnace",
    "SteamReformer": "SteamReformer",
    "MPW2methanol_input": "MPW2methanol"
}


def extract_cc_fractions(result_folder, intervals, location, cc_technologies):
    """
    Extracts carbon capture (CC) fractions for specified technologies from HDF5 result files
    in the cluster model output. Also includes _existing variants automatically.

    Args:
        result_folder (Path): Path to folder with Summary.xlsx and HDF5 results
        intervals (list): List of years (e.g. ["2030", "2040"])
        location (str): Region label (e.g. "Zeeland")
        cc_technologies (dict): Dict of alias -> actual tech name (e.g. {"SteamReformer": "SteamReformer"})

    Returns:
        dict: {(location, interval, tech_alias): cc_fraction} with floats between 0 and 1
    """
    print("Extracting CC fractions for selected technologies (including _existing variants)")

    summary_path = result_folder / "Summary.xlsx"
    try:
        summary_df = pd.read_excel(summary_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing summary: {summary_path}")

    # Step 1: Extend cc_technologies to include _existing variants
    cc_tech_map = {}
    for alias, base_tech in cc_technologies.items():
        cc_tech_map[alias] = base_tech
        cc_tech_map[f"{alias}_existing"] = f"{base_tech}_existing"

    cc_fraction_dict = {}

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
                opdata = extract_datasets_from_h5group(hdf_file["operation/technology_operation"])
                opdata = {k: v for k, v in opdata.items() if len(v) >= 8670}
                df_op = pd.DataFrame(opdata)

                if df_op.columns.nlevels > 2:
                    for tech in df_op.columns.levels[2]:
                        for alias, tech_name in cc_tech_map.items():
                            if tech.startswith(tech_name):
                                col_cc = (interval, location, tech, "CO2captured_output")
                                col_em = (interval, location, tech, "emissions_pos")

                                if col_cc in df_op.columns and col_em in df_op.columns:
                                    numerator = df_op[col_cc].sum()
                                    denominator = numerator + df_op[col_em].sum()
                                    frac_CC = numerator / denominator if (denominator > 1 and numerator > 1) else 0

                                    cc_fraction_dict[(location, interval, alias)] = float(frac_CC)

    return cc_fraction_dict



print(extract_cc_fractions(result_folder, intervals, location, cc_technologies))