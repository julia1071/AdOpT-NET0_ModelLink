# merged_updated_dict_cc = {('Zeeland', '2030', 'CrackerFurnace'): 2516727.272727268, ('Zeeland', '2030', 'ElectricSMR_m'): 365977.9107377938, ('Zeeland', '2030', 'MPW2methanol_output'): 0.0, ('Zeeland', '2030', 'AEC'): 4676430.279057744, ('Zeeland', '2030', 'CO2electrolysis'): 0.0, ('Zeeland', '2030', 'MPW2methanol_input'): 0.0, ('Zeeland', '2030', 'PDH'): 612970.0727272722, ('Zeeland', '2030', 'MPW2methanol_input_CC'): 0.0, ('Zeeland', '2030', 'MTO'): 0.0, ('Zeeland', '2040', 'CrackerFurnace'): 0.0, ('Zeeland', '2040', 'ElectricSMR_m'): 1359458.4762049336, ('Zeeland', '2040', 'MPW2methanol_output'): 1260683.176473579, ('Zeeland', '2040', 'AEC'): 0.0, ('Zeeland', '2040', 'CO2electrolysis'): 1010855.7349471111, ('Zeeland', '2040', 'MPW2methanol_input'): 9444.526598562134, ('Zeeland', '2040', 'PDH'): 292950.1831695437, ('Zeeland', '2040', 'MPW2methanol_input_CC'): 848163.076444689, ('Zeeland', '2040', 'MTO'): 205491.35776519336, ('Zeeland', '2050', 'CrackerFurnace'): 0.0, ('Zeeland', '2050', 'ElectricSMR_m'): 556320.2905021796, ('Zeeland', '2050', 'MPW2methanol_output'): 0.0, ('Zeeland', '2050', 'AEC'): 3931274.7043490848, ('Zeeland', '2050', 'CO2electrolysis'): 1373822.9999999995, ('Zeeland', '2050', 'MPW2methanol_input'): 0.0, ('Zeeland', '2050', 'PDH'): 343486.9999999993, ('Zeeland', '2050', 'MPW2methanol_input_CC'): 0.0, ('Zeeland', '2050', 'MTO'): 0.0}
# bio_ratios = {('Zeeland', '2030'): 0.0, ('Zeeland', '2040'): 0.0, ('Zeeland', '2050'): 0.0}
# bio_tech_names = ["CrackerFurnace_CC", "CrackerFurnace_Electric"]
# location = "Zeeland"


def apply_bio_splitting(merged_tech_size_dict, bio_ratios, bio_tech_names, location):
    """
    Splits selected technologies into bio and non-bio based on the provided ratio,
    even when the ratio is 0, ensuring '_bio' techs are always created.

    Args:
        merged_tech_size_dict (dict): {(location, interval, tech): size}
        bio_ratios (dict): {(location, interval): ratio}
        bio_tech_names (set or list): technologies to split
        location (str): target location

    Returns:
        dict: updated dictionary with _bio and remaining techs
    """
    print(f"The technologies in {bio_tech_names} are splitted into bio and non bio")

    updated_dict_bio = merged_tech_size_dict.copy()

    for (loc, interval, tech) in list(merged_tech_size_dict.keys()):
        if loc != location:
            continue

        if tech in bio_tech_names:
            size = merged_tech_size_dict[(loc, interval, tech)]
            ratio = bio_ratios.get((loc, interval), 0.0)

            if ratio > 0:
                size_bio = size * ratio
                size_non_bio = size * (1 - ratio)

                bio_tech = f"{tech}_bio"

                updated_dict_bio[(loc, interval, bio_tech)] = size_bio
                updated_dict_bio[(loc, interval, tech)] = size_non_bio # overwrite with non-bio part

    return updated_dict_bio

# print(apply_bio_splitting(merged_updated_dict_cc, bio_ratios, bio_tech_names, location))