from pathlib import Path
import pandas as pd
import h5py
from adopt_net0 import extract_datasets_from_h5group


# --- Configuration ---
result_folder = Path("U:/Data AdOpt-NET0/Test/Result path/EL_Chemelot")
intervals = ["2030", "2040", "2050"]
location = "Chemelot"

#Create the dictionary where is stated which technology belongs to which Tech_ID. Check these values when really using.
tech_to_id = {"Boiler_El_existing": "HTI01_16","Boiler_Industrial_NG": "HTI01_01","CrackerFurnace_Electric": "ICH01_05",
              "CrackerFurnace_existing": "ICH01_01" ,"EDH_existing": "ICH01_11","HaberBosch_existing": "Amm01_01"}


def extract_data_cluster(result_folder, intervals, location, tech_to_id):
    # --- Main Process ---
    print("The capacities of the technologies given in tech_to_id are stored in a dictionary updates")
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


    # Print resulting dictionary (optional)
    #for key, value in tech_size_dict.items():
        #print(f"{key}: {value}")


    updates = {}

    for (loc, year, tech), value in tech_size_dict.items():
        tech_id = tech_to_id.get(tech)
        if tech_id is None:
            continue  # or log missing techs
        if tech_id not in updates:
            updates[tech_id] = {}
        updates[tech_id][int(year)] = float((8760/1000000)*value) #Here, a function can be inserted to translate the value to the proper units.
    return(updates)

#print(extract_data_cluster(result_folder, intervals, location, tech_to_id))