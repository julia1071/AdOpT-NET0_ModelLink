import config_model_linking as cfg

def merge_and_group_technologies(tech_dict):
    """
    Merges '_existing' and new technology sizes, then aggregates group-level totals.

    Args:
        tech_dict (dict): {(location, interval, tech): size}

    Returns:
        dict: {(location, interval, tech/group): total size}
    """
    print("Merging '_existing' technologies with their base variants and combining grouped technologies")

    merged_dict = {}

    # Step 1: Merge '_existing' and base technologies
    for (location, interval, tech), value in tech_dict.items():
        base_tech = tech.replace("_existing", "")
        key = (location, interval, base_tech)
        merged_dict[key] = merged_dict.get(key, 0.0) + value

    # Step 2: Add group-level aggregates
    combined_dict = merged_dict.copy()

    for (location, interval, _) in merged_dict.keys():
        for group_alias, alias_list in cfg.group_map.items():
            group_key = (location, interval, group_alias)
            group_sum = sum(
                merged_dict.get((location, interval, alias), 0.0)
                for alias in alias_list
            )
            combined_dict[group_key] = group_sum

    return combined_dict


