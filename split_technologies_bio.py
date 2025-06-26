
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

            size_bio = size * ratio
            size_non_bio = size * (1 - ratio)

            bio_tech = f"{tech}_bio"

            updated_dict_bio[(loc, interval, bio_tech)] = size_bio
            updated_dict_bio[(loc, interval, tech)] = size_non_bio  # overwrite with non-bio part

    return updated_dict_bio


