import config_model_linking as cfg

import numpy as np

def merge_and_group_technologies(tech_dict):
    """
    Merges '_existing' and base technologies, then aggregates grouped outputs per group alias,
    for each data type in the top-level dict (e.g. 'AnnualOutput', 'Operation').

    Args:
        tech_dict (dict): {
            "AnnualOutput": {(location, interval, tech): scalar},
            "Operation": {(location, interval, tech): np.array or list of values}
        }

    Returns:
        dict: {
            "AnnualOutput": {(location, interval, tech/group): value},
            "Operation": {(location, interval, tech/group): value}
        }
    """
    print("🔄 Merging '_existing' technologies and aggregating grouped outputs...")
    merged_output = {}

    for category, subdict in tech_dict.items():
        merged_dict = {}

        if category == "AnnualOutput":
            for (loc, interval, tech), value in subdict.items():
                base_tech = tech.replace("_existing", "")
                key = (loc, interval, base_tech)
                merged_dict[key] = merged_dict.get(key, 0.0) + value

        elif category == "Operation":
            grouped = {}

            for (loc, interval, tech), array in subdict.items():
                base_tech = tech.replace("_existing", "")
                key = (loc, interval, base_tech)

                # Store actual array or None
                grouped.setdefault(key, []).append(np.array(array) if array is not None else None)

            for key, arrays in grouped.items():
                arrays = [a for a in arrays if a is not None]

                if len(arrays) == 2:
                    merged_dict[key] = (arrays[0] + arrays[1]) / 2
                elif len(arrays) == 1:
                    merged_dict[key] = arrays[0]
                else:
                    merged_dict[key] = None

        # Step 2: Aggregate over groups
        combined_dict = merged_dict.copy()
        for (loc, interval, _) in merged_dict:
            for group_alias, tech_list in cfg.group_map.items():
                group_key = (loc, interval, group_alias)

                present_techs = [
                    (loc, interval, tech) for tech in tech_list
                    if (loc, interval, tech) in merged_dict
                ]

                if not present_techs:
                    continue  # Skip this group if none of the techs are present

                if category == "AnnualOutput":
                    group_sum = sum(merged_dict[k] for k in present_techs)
                    combined_dict[group_key] = group_sum

                elif category == "Operation":
                    arrays = [merged_dict[k] for k in present_techs]
                    if arrays:
                        combined_dict[group_key] = np.mean(arrays, axis=0)
                        print("Taking average value for operation for grouped outputs")

        merged_output[category] = combined_dict

    return merged_output



