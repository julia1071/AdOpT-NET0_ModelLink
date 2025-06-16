from conversion_factors import conversion_factor_cluster_to_IESA

# updated_dict_bio = {('Zeeland', '2030', 'CO2_mixer'): 0.0, ('Zeeland', '2030', 'naphtha_mixer'): 0.0, ('Zeeland', '2030', 'AEC'): 0.0, ('Zeeland', '2030', 'MTO'): 0.0, ('Zeeland', '2030', 'SteamReformer'): 0.0, ('Zeeland', '2030', 'DirectMeOHsynthesis'): 0.0, ('Zeeland', '2030', 'OlefinSeparation'): 451.0, ('Zeeland', '2030', 'feedgas_mixer'): 866.3432435006615, ('Zeeland', '2030', 'RWGS'): 0.0, ('Zeeland', '2030', 'MeOHsynthesis'): 0.0, ('Zeeland', '2030', 'MPW2methanol'): 0.0, ('Zeeland', '2030', 'PDH'): 0.0, ('Zeeland', '2030', 'CO2electrolysis'): 0.0, ('Zeeland', '2030', 'syngas_mixer'): 0.0, ('Zeeland', '2030', 'ElectricSMR_m'): 866.3432435006615, ('Zeeland', '2030', 'HBfeed_mixer'): 804.5227223309415, ('Zeeland', '2030', 'CrackerFurnace_Electric'): 446.36797019735565, ('Zeeland', '2030', 'Boiler_El'): 79.85640741754807, ('Zeeland', '2030', 'Storage_H2'): 0.0, ('Zeeland', '2030', 'Storage_Battery'): 0.0, ('Zeeland', '2030', 'WGS_m'): 162.00618653462374, ('Zeeland', '2030', 'CO2toEmission'): 0.0, ('Zeeland', '2030', 'CrackerFurnace'): 0.0, ('Zeeland', '2030', 'Boiler_Industrial_NG'): 0.0, ('Zeeland', '2030', 'EDH'): 0.2933936069255397, ('Zeeland', '2030', 'HaberBosch'): 804.5227223309415, ('Zeeland', '2030', 'ASU'): 27.95716460100022, ('Zeeland', '2030', 'Storage_CO2'): 0.0, ('Zeeland', '2040', 'CO2_mixer'): 0.0, ('Zeeland', '2040', 'naphtha_mixer'): 226.2213431627929, ('Zeeland', '2040', 'AEC'): 0.0, ('Zeeland', '2040', 'MTO'): 0.0, ('Zeeland', '2040', 'SteamReformer'): 0.0, ('Zeeland', '2040', 'DirectMeOHsynthesis'): 0.0, ('Zeeland', '2040', 'OlefinSeparation'): 451.0, ('Zeeland', '2040', 'feedgas_mixer'): 866.3432435006615, ('Zeeland', '2040', 'RWGS'): 0.0, ('Zeeland', '2040', 'MeOHsynthesis'): 0.0, ('Zeeland', '2040', 'MPW2methanol'): 0.0, ('Zeeland', '2040', 'PDH'): 0.0, ('Zeeland', '2040', 'CO2electrolysis'): 0.0, ('Zeeland', '2040', 'syngas_mixer'): 0.0, ('Zeeland', '2040', 'ElectricSMR_m'): 866.3432435006615, ('Zeeland', '2040', 'HBfeed_mixer'): 804.5227223309415, ('Zeeland', '2040', 'CrackerFurnace_Electric'): 446.36797019735565, ('Zeeland', '2040', 'Boiler_El'): 79.85640741754807, ('Zeeland', '2040', 'Storage_H2'): 0.0, ('Zeeland', '2040', 'Storage_Battery'): 0.0, ('Zeeland', '2040', 'WGS_m'): 162.00618653462374, ('Zeeland', '2040', 'CO2toEmission'): 0.0, ('Zeeland', '2040', 'CrackerFurnace'): 0.0, ('Zeeland', '2040', 'Boiler_Industrial_NG'): 0.0, ('Zeeland', '2040', 'EDH'): 0.2933936069255397, ('Zeeland', '2040', 'HaberBosch'): 804.5227223309415, ('Zeeland', '2040', 'ASU'): 27.95716460100022, ('Zeeland', '2040', 'Storage_CO2'): 0.0, ('Zeeland', '2050', 'CO2_mixer'): 0.0, ('Zeeland', '2050', 'naphtha_mixer'): 446.36797019735536, ('Zeeland', '2050', 'AEC'): 0.0, ('Zeeland', '2050', 'MTO'): 0.0, ('Zeeland', '2050', 'SteamReformer'): 0.0, ('Zeeland', '2050', 'DirectMeOHsynthesis'): 0.0, ('Zeeland', '2050', 'OlefinSeparation'): 451.0, ('Zeeland', '2050', 'feedgas_mixer'): 866.3432435006615, ('Zeeland', '2050', 'RWGS'): 0.0, ('Zeeland', '2050', 'MeOHsynthesis'): 0.0, ('Zeeland', '2050', 'MPW2methanol'): 0.0, ('Zeeland', '2050', 'PDH'): 0.0, ('Zeeland', '2050', 'CO2electrolysis'): 0.0, ('Zeeland', '2050', 'syngas_mixer'): 0.0, ('Zeeland', '2050', 'ElectricSMR_m'): 866.3432435006615, ('Zeeland', '2050', 'HBfeed_mixer'): 804.5227223309415, ('Zeeland', '2050', 'CrackerFurnace_Electric'): 446.36797019735565, ('Zeeland', '2050', 'Boiler_El'): 79.85640741754807, ('Zeeland', '2050', 'Storage_H2'): 0.0, ('Zeeland', '2050', 'Storage_Battery'): 0.0, ('Zeeland', '2050', 'WGS_m'): 162.00618653462374, ('Zeeland', '2050', 'CO2toEmission'): 0.0, ('Zeeland', '2050', 'CrackerFurnace'): 0.0, ('Zeeland', '2050', 'Boiler_Industrial_NG'): 0.0, ('Zeeland', '2050', 'EDH'): 0.2933936069255397, ('Zeeland', '2050', 'HaberBosch'): 804.5227223309415, ('Zeeland', '2050', 'ASU'): 27.95716460100022, ('Zeeland', '2050', 'Storage_CO2'): 0.0, ('Zeeland', '2030', 'CrackerFurnace_Electric_bio'): 0.0, ('Zeeland', '2040', 'CrackerFurnace_Electric_bio'): 0.0, ('Zeeland', '2050', 'CrackerFurnace_Electric_bio'): 0.0}
# tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03", "CrackerFurnace_Electric": "ICH01_05",
#               "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11", "MTO": "ICH01_12", "PDH": "ICH01_14", "MPW2methanol": ["WAI01_10","RFS04_01"],
#               "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
#                 "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
#               }

def map_techs_to_ID(updated_dict_bio, tech_to_id):
    """
    Maps technology names to technology IDs, supports one-to-many mappings,
    applies tech-specific unit conversion, and ensures all tech_IDs are present.

    Args:
        updated_dict_bio (dict): {(location, year, tech_name): value}
        tech_to_id (dict): {tech_name: tech_id or list of tech_ids}

    Returns:
        dict: {tech_id: {year: converted_value}}
    """
    print("The technologies are mapped based on their corresponding Tech_ID and conversion factor.")
    updates = {}

    # Collect all years seen in the input
    all_years = sorted({int(year) for (_, year, _) in updated_dict_bio.keys()})

    # Process input values and apply conversion
    for (loc, year, tech), value in updated_dict_bio.items():
        tech_ids = tech_to_id.get(tech)
        if tech_ids is None:
            continue  # Optionally warn

        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            try:
                conversion = conversion_factor_cluster_to_IESA(tech_id)
            except ValueError as e:
                print(e)
                continue

            scaled_value = float(value) * conversion

            if tech_id not in updates:
                updates[tech_id] = {}
            updates[tech_id][int(year)] = scaled_value

    # Ensure all tech_IDs exist for all years, fill with 0.0 if needed
    for tech_name, tech_ids in tech_to_id.items():
        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            if tech_id not in updates:
                print(f"Note: No input found for Tech_ID '{tech_id}' (from tech '{tech_name}'), setting all years to 0.")
                updates[tech_id] = {}

            for year in all_years:
                updates[tech_id].setdefault(year, 0.0)

    return updates

# print(map_techs_to_ID(updated_dict_bio, tech_to_id))