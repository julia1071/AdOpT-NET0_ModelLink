from conversion_factors import conversion_factor_cluster_to_IESA

# updated_dict_bio = {('Zeeland', '2030', 'CrackerFurnace'): 2516727.272727268, ('Zeeland', '2030', 'ElectricSMR_m'): 365977.9107377938, ('Zeeland', '2030', 'MPW2methanol_output'): 0.0, ('Zeeland', '2030', 'AEC'): 4676430.279057744, ('Zeeland', '2030', 'CO2electrolysis'): 0.0, ('Zeeland', '2030', 'MPW2methanol_input'): 0.0, ('Zeeland', '2030', 'PDH'): 612970.0727272722, ('Zeeland', '2030', 'MPW2methanol_input_CC'): 0.0, ('Zeeland', '2030', 'MTO'): 0.0, ('Zeeland', '2040', 'CrackerFurnace'): 0.0, ('Zeeland', '2040', 'ElectricSMR_m'): 1359458.4762049336, ('Zeeland', '2040', 'MPW2methanol_output'): 1260683.176473579, ('Zeeland', '2040', 'AEC'): 0.0, ('Zeeland', '2040', 'CO2electrolysis'): 1010855.7349471111, ('Zeeland', '2040', 'MPW2methanol_input'): 9444.526598562134, ('Zeeland', '2040', 'PDH'): 292950.1831695437, ('Zeeland', '2040', 'MPW2methanol_input_CC'): 848163.076444689, ('Zeeland', '2040', 'MTO'): 205491.35776519336, ('Zeeland', '2050', 'CrackerFurnace'): 0.0, ('Zeeland', '2050', 'ElectricSMR_m'): 556320.2905021796, ('Zeeland', '2050', 'MPW2methanol_output'): 0.0, ('Zeeland', '2050', 'AEC'): 3931274.7043490848, ('Zeeland', '2050', 'CO2electrolysis'): 1373822.9999999995, ('Zeeland', '2050', 'MPW2methanol_input'): 0.0, ('Zeeland', '2050', 'PDH'): 343486.9999999993, ('Zeeland', '2050', 'MPW2methanol_input_CC'): 0.0, ('Zeeland', '2050', 'MTO'): 0.0}
# tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03", "CrackerFurnace_Electric": "ICH01_05",
#               "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11", "MTO": "ICH01_12", "PDH": "ICH01_14", "MPW2methanol": ["WAI01_10","RFS04_01"],
#               "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
#                 "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
#               }

def map_techs_to_ID(updated_dict_bio, tech_to_id):
    """
    Maps technology names to technology IDs, supports one-to-many mappings,
    applies tech-specific unit conversion, and returns only non-zero values per Tech_ID.

    Args:
        updated_dict_bio (dict): {(location, year, tech_name): value}
        tech_to_id (dict): {tech_name: tech_id or list of tech_ids}

    Returns:
        dict: {tech_id: {year: converted_value}}, only for non-zero values
    """
    print("The technologies are mapped based on their corresponding Tech_ID and conversion factor.")
    updates = {}

    # Collect all years seen in the input
    all_years = sorted({int(year) for (_, year, _) in updated_dict_bio.keys()})

    # Process input values and apply conversion
    for (loc, year, tech), value in updated_dict_bio.items():
        tech_ids = tech_to_id.get(tech)
        if tech_ids is None:
            continue  # Tech not mapped

        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            try:
                conversion = conversion_factor_cluster_to_IESA(tech_id)
            except ValueError as e:
                print(e)
                continue

            scaled_value = float(value) * conversion
            if scaled_value == 0.0:
                continue  # Skip storing zeroes

            if tech_id not in updates:
                updates[tech_id] = {}
            updates[tech_id][int(year)] = scaled_value

    return updates


# print(map_techs_to_ID(updated_dict_bio, tech_to_id))