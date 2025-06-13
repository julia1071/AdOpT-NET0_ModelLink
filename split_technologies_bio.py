
def apply_bio_split(tech_size_dict, bio_ratios, bio_tech_names, location):
    """
    Splits selected technologies into bio and non-bio based on the provided ratio,
    even when the ratio is 0, ensuring '_bio' techs are always created.

    Args:
        tech_size_dict (dict): {(location, interval, tech): size}
        bio_ratios (dict): {(location, interval): ratio}
        bio_tech_names (set or list): technologies to split (e.g., {'CrackerFurnace_CC', ...})
        location (str): target location (e.g., "Zeeland")

    Returns:
        dict: updated dictionary with _bio and remaining techs
    """
    updated_dict = tech_size_dict.copy()

    for (loc, interval, tech) in list(tech_size_dict.keys()):
        if loc != location:
            continue

        if tech in bio_tech_names:
            size = tech_size_dict[(loc, interval, tech)]
            ratio = bio_ratios.get((loc, interval), 0.0)

            size_bio = size * ratio
            size_non_bio = size * (1 - ratio)

            bio_tech = f"{tech}_bio"

            updated_dict[(loc, interval, bio_tech)] = size_bio
            updated_dict[(loc, interval, tech)] = size_non_bio  # overwrite with non-bio part

    return updated_dict

tech_size_dict = {
    ('Zeeland', '2030', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2030', 'Storage_CO2'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol'): 0.0,
    ('Zeeland', '2030', 'CO2toEmission'): 0.0,
    ('Zeeland', '2030', 'EDH'): 0.0,
    ('Zeeland', '2030', 'AEC'): 0.0,
    ('Zeeland', '2030', 'PDH'): 0.0,
    ('Zeeland', '2030', 'Storage_Battery'): 0.0,
    ('Zeeland', '2030', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2030', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2030', 'RWGS'): 0.0,
    ('Zeeland', '2030', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2030', 'HaberBosch'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2030', 'syngas_mixer'): 0.0,
    ('Zeeland', '2030', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2030', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'ASU'): 0.0,
    ('Zeeland', '2030', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2030', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2030', 'Boiler_El'): 0.0,
    ('Zeeland', '2030', 'MTO'): 0.0,
    ('Zeeland', '2030', 'SteamReformer'): 105.71914879513074,
    ('Zeeland', '2030', 'MPW2methanol_CC'): 0.0,
    ('Zeeland', '2030', 'CO2_mixer'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_CC'): 0.0,
    ('Zeeland', '2030', 'Storage_H2'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_CC'): 0.0,
    ('Zeeland', '2030', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2030', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'WGS_m'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2040', 'Storage_CO2'): 4481.695179214337,
    ('Zeeland', '2040', 'MPW2methanol'): 0.8657755491526394,
    ('Zeeland', '2040', 'CO2toEmission'): 0.0,
    ('Zeeland', '2040', 'EDH'): 136.46232791347748,
    ('Zeeland', '2040', 'AEC'): 0.0,
    ('Zeeland', '2040', 'PDH'): 36.97144365819727,
    ('Zeeland', '2040', 'Storage_Battery'): 5513.499928117991,
    ('Zeeland', '2040', 'Boiler_Industrial_NG'): 386.7784939674664,
    ('Zeeland', '2040', 'CO2electrolysis'): 206.9747557802476,
    ('Zeeland', '2040', 'RWGS'): 0.0,
    ('Zeeland', '2040', 'ElectricSMR_m'): 1917.3486711614985,
    ('Zeeland', '2040', 'HaberBosch'): 80.45227228817883,
    ('Zeeland', '2040', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2040', 'syngas_mixer'): 358.5442015072002,
    ('Zeeland', '2040', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2040', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2040', 'ASU'): 2.795716447419882,
    ('Zeeland', '2040', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2040', 'feedgas_mixer'): 2026.3765796917955,
    ('Zeeland', '2040', 'Boiler_El'): 532.0052720677872,
    ('Zeeland', '2040', 'MTO'): 392.649098245147,
    ('Zeeland', '2040', 'SteamReformer'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_CC'): 65.50648322956928,
    ('Zeeland', '2040', 'CO2_mixer'): 289.6016557730147,
    ('Zeeland', '2040', 'CrackerFurnace_CC'): 0.0,
    ('Zeeland', '2040', 'Storage_H2'): 6.109531913381054e-08,
    ('Zeeland', '2040', 'SteamReformer_CC'): 0.0,
    ('Zeeland', '2040', 'HBfeed_mixer'): 80.45227231021265,
    ('Zeeland', '2040', 'MeOHsynthesis'): 492.33040574777795,
    ('Zeeland', '2040', 'WGS_m'): 13.889717300760989,
    ('Zeeland', '2050', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2050', 'Storage_CO2'): 0.0,
    ('Zeeland', '2050', 'MPW2methanol'): 0.0,
    ('Zeeland', '2050', 'CO2toEmission'): 0.0,
    ('Zeeland', '2050', 'EDH'): 0.0,
    ('Zeeland', '2050', 'AEC'): 0.0,
    ('Zeeland', '2050', 'PDH'): 0.0,
    ('Zeeland', '2050', 'Storage_Battery'): 0.0,
    ('Zeeland', '2050', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2050', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2050', 'RWGS'): 0.0,
    ('Zeeland', '2050', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2050', 'HaberBosch'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2050', 'syngas_mixer'): 0.0,
    ('Zeeland', '2050', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2050', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2050', 'ASU'): 0.0,
    ('Zeeland', '2050', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2050', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2050', 'Boiler_El'): 0.0,
    ('Zeeland', '2050', 'MTO'): 0.0,
    ('Zeeland', '2050', 'SteamReformer'): 0.0,
    ('Zeeland', '2050', 'MPW2methanol_CC'): 0.0,
    ('Zeeland', '2050', 'CO2_mixer'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_CC'): 0.0,
    ('Zeeland', '2050', 'Storage_H2'): 0.0,
    ('Zeeland', '2050', 'SteamReformer_CC'): 0.0,
    ('Zeeland', '2050', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2050', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2050', 'WGS_m'): 0.0
}

bio_ratio_dict = {('Zeeland', '2030'): 0.0, ('Zeeland', '2040'): 0.0}
bio_naphtha_techs = ["CrackerFurnace_CC", "CrackerFurnace_Electric"]
location = "Zeeland"

print(apply_bio_split(tech_size_dict, bio_ratio_dict, bio_naphtha_techs, location))
