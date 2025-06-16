


def merge_existing_and_new_techs(tech_size_dict, intervals, location):
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
    print("The existing technologies and the new technologies will be merged as one and the same technology")

    merged_tech_size_dict = {}

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
            merged_tech_size_dict[merged_key] = value_std + value_ext

    return merged_tech_size_dict
