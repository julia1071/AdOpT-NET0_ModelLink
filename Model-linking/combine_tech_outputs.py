def combine_tech_outputs(merged_tech_output_dict, group_map):
    """
    Combines the values of multiple technology aliases into new grouped aliases.

    Args:
        merged_tech_output_dict (dict): Dictionary with keys (location, interval, tech_alias) and float values
        group_map (dict): Dictionary where keys are new group names and values are lists of aliases to sum

    Returns:
        dict: Updated dictionary with combined aliases added
    """
    combined_dict = merged_tech_output_dict.copy()

    for (location, interval, _) in merged_tech_output_dict.keys():
        for group_alias, alias_list in group_map.items():
            group_key = (location, interval, group_alias)
            group_sum = 0.0

            for alias in alias_list:
                tech_key = (location, interval, alias)
                if tech_key in merged_tech_output_dict:
                    group_sum += merged_tech_output_dict[tech_key]

            combined_dict[group_key] = group_sum

    return combined_dict

merged_tech_output_dict = {
    ("Zeeland", "2030", "MPW2methanol_output"): 1000.0,
    ("Zeeland", "2030", "MeOH_synthesis"): 500.0,
    ("Zeeland", "2030", "Biomass_gasification"): 200.0,
}

group_map = {
    "methanol_from_syngas": [
        "MPW2methanol_output",
        "MeOH_synthesis",
        "Biomass_gasification"
    ]
}