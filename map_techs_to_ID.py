#Create the dictionary where is stated which technology belongs to which Tech_ID. Check these values when really using.
tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03", "CrackerFurnace_Electric": "ICH01_05",
              "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11", "MTO": "ICH01_12", "PDH": "ICH01_14", "MPW2methanol": ["WAI01_10","RFS04_01"],
              "RWGS": "HTI01_16", "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
                "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
              }

def map_techs_to_ID(tech_size_dict, tech_to_id):
    """
    Maps technology names to technology IDs, supporting one-to-many mappings.

    Args:
        tech_size_dict (dict): Dictionary with keys (location, year, tech_name) and float values.
        tech_to_id (dict): Mapping from tech_name to one or more tech_ids (string or list of strings).

    Returns:
        dict: Nested dictionary of the form {tech_id: {year: value}}.
    """
    updates = {}

    for (loc, year, tech), value in tech_size_dict.items():
        tech_ids = tech_to_id.get(tech)

        if tech_ids is None:
            continue  # Optionally log: print(f"Missing mapping for {tech}")

        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            if tech_id not in updates:
                updates[tech_id] = {}

            updates[tech_id][int(year)] = float(value) #Insert conversion function here!

    return updates