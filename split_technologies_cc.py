
def apply_cc_splitting(tech_size_dict, cc_fraction_dict, capture_rate):
    """
    For each technology in cc_fraction_dict:
    - Splits the value in tech_size_dict into a CC and non-CC part.
    - Adds a new entry with name `technology_CC` or `technology_CC_existing`
    - Updates the original entry to its non-CC share.

    Returns a new updated dictionary.
    """
    print("The technologies dictionary will be splitted to carbon capture and non carbon capture")

    updated_dict_cc = tech_size_dict.copy()

    for (location, interval, tech), cc_frac in cc_fraction_dict.items():
        if (location, interval, tech) not in tech_size_dict:
            print(f"No original size of {tech} in {tech_size_dict}")

        original_size = tech_size_dict[(location, interval, tech)]

        # Calculate shares
        cc_ratio = cc_frac / capture_rate
        non_cc_ratio = 1 - cc_ratio

        size_cc = original_size * cc_ratio
        size_non_cc = original_size * non_cc_ratio

        # Build new tech name (preserve "_existing" if present)
        if tech.endswith("_existing"):
            base_tech = tech.replace("_existing", "")
            new_tech = f"{base_tech}_CC_existing"
        else:
            new_tech = f"{tech}_CC"

        # Add to updated dictionary
        updated_dict_cc[(location, interval, new_tech)] = size_cc
        updated_dict_cc[(location, interval, tech)] = size_non_cc  # overwrite

    return updated_dict_cc
