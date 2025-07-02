updated_dict_cc = {('Zeeland', '2030', 'CrackerFurnace'): 2516727.272727268, ('Zeeland', '2030', 'PDH'): 612970.0727272722, ('Zeeland', '2030', 'AEC'): 4676430.279057744, ('Zeeland', '2030', 'ElectricSMR_m'): 365977.9107377938, ('Zeeland', '2040', 'MTO'): 205491.35776519336, ('Zeeland', '2040', 'PDH_existing'): 292950.1831695437, ('Zeeland', '2040', 'MPW2methanol_input'): 9444.526598562134, ('Zeeland', '2040', 'MPW2methanol_output'): 1260683.176473579, ('Zeeland', '2040', 'ElectricSMR_m'): 999788.7071749736, ('Zeeland', '2040', 'ElectricSMR_m_existing'): 359669.7690299599, ('Zeeland', '2040', 'CO2electrolysis'): 1010855.7349471111, ('Zeeland', '2050', 'PDH_existing'): 343486.9999999993, ('Zeeland', '2050', 'AEC_existing'): 3931274.7043490848, ('Zeeland', '2050', 'ElectricSMR_m_existing'): 556320.2905021796, ('Zeeland', '2050', 'CO2electrolysis'): 332427.648207849, ('Zeeland', '2050', 'CO2electrolysis_existing'): 1041395.3517921506, ('Zeeland', '2040', 'MPW2methanol_input_CC'): 848163.076444689}
intervals =['2030','2040','2050']
location = "Zeeland"

def merge_existing_and_new_techs(updated_dict_cc, intervals, location):
    """
    Merges technology sizes by summing each base technology with its '_existing' counterpart
    for a given location and a list of intervals.

    Args:
        updated_dict_cc (dict): Dictionary with keys (location, interval, tech) -> output
        intervals (list): List of interval strings
        location (str): The location to filter on

    Returns:
        dict: New dictionary with merged keys (location, interval, base_tech) -> total size
    """
    print("The existing technologies and the new technologies will be merged as one and the same technology")

    merged_updated_dict_cc = {}

    # Step 1: Collect all base tech names (remove _existing)
    tech_names = set()
    for (_, _, tech) in updated_dict_cc.keys():
        base_tech = tech.replace("_existing", "")
        tech_names.add(base_tech)

    # Step 2: Sum values for each base tech and interval
    for interval in intervals:
        for base_tech in tech_names:
            key_std = (location, interval, base_tech)
            key_ext = (location, interval, base_tech + "_existing")

            value_std = updated_dict_cc.get(key_std, 0.0)
            value_ext = updated_dict_cc.get(key_ext, 0.0)

            merged_key = (location, interval, base_tech)
            merged_updated_dict_cc[merged_key] = value_std + value_ext

    return merged_updated_dict_cc

print(merge_existing_and_new_techs(updated_dict_cc,intervals,location))