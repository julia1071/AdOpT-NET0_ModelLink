



def merge_existing_and_new_tech(tech_size_dict, intervals, location):
    """
    Merges technology sizes by summing each base technology with its '_existing' counterpart
    for a given location and a list of intervals.

    Args:
        tech_size_dict (dict): Dictionary with keys (location, interval, tech) -> size
        intervals (list): List of interval strings (e.g., ["2030", "2040", "2050"])
        location (str): The location to filter on (e.g., "Zeeland")

    Returns:
        dict: New dictionary with merged keys (location, interval, base_tech) -> total size
    """
    merged_dict = {}

    # Step 1: Collect all base tech names (remove _existing)
    tech_names = set()
    for (_, _, tech) in tech_size_dict.keys():
        base_tech = tech.replace("_existing", "")
        tech_names.add(base_tech)

    # Step 2: Sum values for each base tech and interval
    for interval in intervals:
        for base_tech in tech_names:
            key_std = (location, interval, base_tech)
            key_ext = (location, interval, base_tech + "_existing")

            value_std = tech_size_dict.get(key_std, 0.0)
            value_ext = tech_size_dict.get(key_ext, 0.0)

            merged_key = (location, interval, base_tech)
            merged_dict[merged_key] = value_std + value_ext

    return merged_dict

intervals = ["2030", "2040", "2050"]
location = "Zeeland"
tech_size_dict = {
    ('Zeeland', '2030', 'AEC'): 0.0,
    ('Zeeland', '2040', 'AEC'): 0.0,
    ('Zeeland', '2050', 'AEC'): 0.0,
    ('Zeeland', '2030', 'ASU'): 0.0,
    ('Zeeland', '2040', 'ASU'): 2.795716447419882,
    ('Zeeland', '2050', 'ASU'): 0.0,
    ('Zeeland', '2030', 'Boiler_El'): 0.0,
    ('Zeeland', '2040', 'Boiler_El'): 0.0,
    ('Zeeland', '2050', 'Boiler_El'): 0.0,
    ('Zeeland', '2030', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2040', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2050', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2030', 'CO2_mixer'): 0.0,
    ('Zeeland', '2040', 'CO2_mixer'): 209.01909638977068,
    ('Zeeland', '2050', 'CO2_mixer'): 0.0,
    ('Zeeland', '2030', 'CO2toEmission'): 0.0,
    ('Zeeland', '2040', 'CO2toEmission'): 0.0,
    ('Zeeland', '2050', 'CO2toEmission'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2030', 'EDH'): 0.0,
    ('Zeeland', '2040', 'EDH'): 0.0,
    ('Zeeland', '2050', 'EDH'): 0.0,
    ('Zeeland', '2030', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2040', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2050', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2030', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2040', 'HBfeed_mixer'): 80.45227231021265,
    ('Zeeland', '2050', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2030', 'HaberBosch'): 0.0,
    ('Zeeland', '2040', 'HaberBosch'): 5.508454311444429e-08,
    ('Zeeland', '2050', 'HaberBosch'): 0.0,
    ('Zeeland', '2030', 'HaberBosch_existing'): 0.0,
    ('Zeeland', '2040', 'HaberBosch_existing'): 80.45227223309429,
    ('Zeeland', '2050', 'HaberBosch_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol'): 0.0,
    ('Zeeland', '2050', 'MPW2methanol'): 0.0,
    ('Zeeland', '2030', 'MTO'): 0.0,
    ('Zeeland', '2040', 'MTO'): 0.0,
    ('Zeeland', '2050', 'MTO'): 0.0,
    ('Zeeland', '2030', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2040', 'MeOHsynthesis'): 133.78620424057752,
    ('Zeeland', '2050', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2040', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2050', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2030', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2040', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2050', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2030', 'PDH'): 0.0,
    ('Zeeland', '2040', 'PDH'): 36.97144365819727,
    ('Zeeland', '2050', 'PDH'): 0.0,
    ('Zeeland', '2030', 'RWGS'): 0.0,
    ('Zeeland', '2040', 'RWGS'): 0.0,
    ('Zeeland', '2050', 'RWGS'): 0.0,
    ('Zeeland', '2030', 'SteamReformer'): 105.71914879513074,
    ('Zeeland', '2040', 'SteamReformer'): 0.0,
    ('Zeeland', '2050', 'SteamReformer'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2040', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2050', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_Battery'): 0.0,
    ('Zeeland', '2040', 'Storage_Battery'): 4065.0,
    ('Zeeland', '2050', 'Storage_Battery'): 0.0,
    ('Zeeland', '2030', 'Storage_CO2'): 0.0,
    ('Zeeland', '2040', 'Storage_CO2'): 0.0,
    ('Zeeland', '2050', 'Storage_CO2'): 0.0,
    ('Zeeland', '2030', 'Storage_H2'): 0.0,
    ('Zeeland', '2040', 'Storage_H2'): 6.109531913381054e-08,
    ('Zeeland', '2050', 'Storage_H2'): 0.0,
    ('Zeeland', '2030', 'WGS_m'): 0.0,
    ('Zeeland', '2040', 'WGS_m'): 13.889717300760989,
    ('Zeeland', '2050', 'WGS_m'): 0.0,
    ('Zeeland', '2030', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2040', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2050', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2030', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2040', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2050', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2030', 'syngas_mixer'): 0.0,
    ('Zeeland', '2040', 'syngas_mixer'): 0.0,
    ('Zeeland', '2050', 'syngas_mixer'): 0.0,
    ('Zeeland', '2030', 'Boiler_El_existing'): 0.0,
    ('Zeeland', '2040', 'Boiler_El_existing'): 532.0052720677872,
    ('Zeeland', '2050', 'Boiler_El_existing'): 0.0,
    ('Zeeland', '2030', 'Boiler_Industrial_NG_existing'): 0.0,
    ('Zeeland', '2040', 'Boiler_Industrial_NG_existing'): 386.7784939674664,
    ('Zeeland', '2050', 'Boiler_Industrial_NG_existing'): 0.0,
    ('Zeeland', '2030', 'CO2_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'CO2_mixer_existing'): 80.58255938324403,
    ('Zeeland', '2050', 'CO2_mixer_existing'): 0.0,
    ('Zeeland', '2030', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2040', 'CO2electrolysis'): 206.9747557802476,
    ('Zeeland', '2050', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2030', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2040', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2050', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'EDH_existing'): 0.0,
    ('Zeeland', '2040', 'EDH_existing'): 136.46232791347748,
    ('Zeeland', '2050', 'EDH_existing'): 0.0,
    ('Zeeland', '2030', 'ElectricSMR_m_existing'): 0.0,
    ('Zeeland', '2040', 'ElectricSMR_m_existing'): 1917.3486711614985,
    ('Zeeland', '2050', 'ElectricSMR_m_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol_existing'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_existing'): 0.8657755491526394,
    ('Zeeland', '2050', 'MPW2methanol_existing'): 0.0,
    ('Zeeland', '2030', 'MTO_existing'): 0.0,
    ('Zeeland', '2040', 'MTO_existing'): 392.649098245147,
    ('Zeeland', '2050', 'MTO_existing'): 0.0,
    ('Zeeland', '2030', 'MeOHsynthesis_existing'): 0.0,
    ('Zeeland', '2040', 'MeOHsynthesis_existing'): 358.54420150720046,
    ('Zeeland', '2050', 'MeOHsynthesis_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_Battery_existing'): 0.0,
    ('Zeeland', '2040', 'Storage_Battery_existing'): 1448.4999281179907,
    ('Zeeland', '2050', 'Storage_Battery_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_CO2_existing'): 0.0,
    ('Zeeland', '2040', 'Storage_CO2_existing'): 4481.695179214337,
    ('Zeeland', '2050', 'Storage_CO2_existing'): 0.0,
    ('Zeeland', '2030', 'feedgas_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'feedgas_mixer_existing'): 2026.3765796917955,
    ('Zeeland', '2050', 'feedgas_mixer_existing'): 0.0,
    ('Zeeland', '2030', 'syngas_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'syngas_mixer_existing'): 358.5442015072002,
    ('Zeeland', '2050', 'syngas_mixer_existing'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_CC'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_CC_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol_CC'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_CC'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_CC_existing'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_CC'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_CC_existing'): 65.50648322956928,
    ('Zeeland', '2040', 'SteamReformer_CC_existing'): 0.0
}


print(merge_existing_and_new_tech(tech_size_dict, intervals, location))