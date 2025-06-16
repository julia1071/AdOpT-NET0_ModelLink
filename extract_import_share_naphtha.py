
import h5py
import pandas as pd
from pathlib import Path
from adopt_net0 import extract_datasets_from_h5group

def extract_import_bio_ratios_naphtha(result_folder, intervals, location):
    """
    Extracts the bio naphtha import ratio per interval (not averaged across cases).

    Args:
        result_folder (Path or str): Folder containing Summary.xlsx and h5 result folders
        intervals (list of str): Intervals, e.g., ["2030", "2040", "2050"]
        location (str): Location node (e.g., "Zeeland")

    Returns:
        dict: {(location, interval): ratio}, only for intervals with available data
    """

    summary_path = result_folder / "Summary.xlsx"

    try:
        summary_df = pd.read_excel(summary_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing summary file: {summary_path}")

    bio_ratios = {}

    for _, row in summary_df.iterrows():
        case = row.get("case")
        if pd.isna(case):
            continue

        for interval in intervals:
            if interval not in case:
                continue

            h5_path = result_folder / row["time_stamp"] / "optimization_results.h5"
            if not h5_path.exists():
                print(f"Missing h5 file: {h5_path}")
                continue

            try:
                with h5py.File(h5_path, "r") as hdf_file:
                    ebalance = extract_datasets_from_h5group(hdf_file["operation/energy_balance"])
                    df_ebalance = pd.DataFrame(ebalance)
            except Exception as e:
                print(f"Error reading {h5_path}: {e}")
                continue

            col_bio = (interval, location, "bio_naphtha", "import")
            col_fossil = (interval, location, "naphtha", "import")

            if col_bio in df_ebalance.columns:
                bio_val = df_ebalance[col_bio].sum()
            else:
                print(f"No bio naphtha import value found for: {col_bio}")
                bio_val = 0

            if col_fossil in df_ebalance.columns:
                foss_val = df_ebalance[col_fossil].sum()
            else:
                print(f"No fossil naphtha import value found for: {col_fossil}")
                foss_val = 0

            total = bio_val + foss_val

            if total > 0:
                ratio = bio_val / total
            else:
                ratio = 0

            # Store the first valid ratio per interval
            bio_ratios[(location, interval)] = float(ratio)

    print(f"The import bio_ratios of bio naphtha/naptha for each interval are extracted: {bio_ratios}")
    return bio_ratios
