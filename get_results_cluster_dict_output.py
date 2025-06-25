
import h5py
import pandas as pd
from pathlib import Path
from adopt_net0 import extract_datasets_from_h5group

result_folder = Path("U:\Data AdOpt-NET0\Model_Linking_simplified\Results\Zeeland\Results_model_linking_20250624_17_38\Iteration_1")
intervals =['2030','2040','2050']
location = "Zeeland"
base_tech_output_map = {
    "CrackerFurnace": "olefins_output",
    "CrackerFurnace_Electric": "olefins_output",
    "MTO": "ethylene_output",
    "PDH": "propylene_output",
    "MPW2methanol": "methanol_output",
    "SteamReformer": "HBfeed_output",
    "AEC": "hydrogen_output",
    "ElectricSMR_m": "syngas_r_output",
    "CO2electrolysis": "ethylene_output",
}


def extract_technology_outputs(base_tech_output_map, result_folder, intervals, location):
    print("Extracting technology outputs from cluster model")

    summary_path = result_folder / "Summary.xlsx"
    try:
        summary_df = pd.read_excel(summary_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing summary: {summary_path}")

    # Add _existing variants
    tech_output_map = base_tech_output_map.copy()
    for tech, output in base_tech_output_map.items():
        tech_output_map[f"{tech}_existing"] = output

    tech_output_dict = {}

    for _, row in summary_df.iterrows():
        case = row["case"]
        if pd.isna(case):
            continue

        matched_interval = next((i for i in intervals if i in case), None)
        if matched_interval is None:
            continue

        h5_path = result_folder / row["time_stamp"] / "optimization_results.h5"
        if not h5_path.exists():
            print(f"Missing h5 file: {h5_path}")
            continue

        with h5py.File(h5_path, "r") as hdf_file:
            tec_operation = extract_datasets_from_h5group(hdf_file["operation/technology_operation"])
            tec_operation = {k: v for k, v in tec_operation.items() if len(v) >= 8670}
            df_op = pd.DataFrame(tec_operation)

            if df_op.columns.nlevels > 2:
                for tech in df_op.columns.levels[2]:
                    output_col_name = None
                    for prefix, output_name in tech_output_map.items():
                        if tech.startswith(prefix):
                            output_col_name = output_name
                            break
                    if not output_col_name:
                        continue

                    col = (matched_interval, location, tech, output_col_name)
                    if col in df_op.columns:
                        total_output = df_op[col].sum()
                        tech_output_dict[(location, matched_interval, tech)] = float(total_output)
    return tech_output_dict



print(extract_technology_outputs(base_tech_output_map, result_folder,intervals, location))