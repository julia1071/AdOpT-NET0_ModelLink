# cc_fraction_dict = {('Zeeland', '2030', 'CrackerFurnace'): 0.8, ('Zeeland', '2030', 'CrackerFurnace_existing'): 0.6, ('Zeeland', '2030', 'MPW2methanol_input'): 0.4, ('Zeeland', '2030', 'SteamReformer'): 0.3, ('Zeeland', '2030', 'SteamReformer_existing'): 0.6}
# tech_output_dict = {('Zeeland', '2030', 'CrackerFurnace'): 0.0, ('Zeeland', '2030', 'CrackerFurnace_existing'): 0.0, ('Zeeland', '2030', 'CrackerFurnace_Electric'): 0.0, ('Zeeland', '2030', 'MTO'): 524400.0000000002, ('Zeeland', '2030', 'PDH'): 662075.6441717829, ('Zeeland', '2030', 'MPW2methanol_input'): 2188556.404156755, ('Zeeland', '2030', 'MPW2methanol_output'): 3217177.9141104314, ('Zeeland', '2030', 'SteamReformer'): 0.0, ('Zeeland', '2030', 'SteamReformer_existing'): 0.0, ('Zeeland', '2030', 'AEC'): 2693061.8605810967, ('Zeeland', '2030', 'ElectricSMR_m'): 756434.5403899723}
# capture_rate = 0.9


def apply_cc_splitting(tech_output_dict, cc_fraction_dict, capture_rate):
    """
    Splits technologies into carbon capture (CC) and non-CC variants based on capture fractions
    and a specified maximum capture rate.

    Args:
        tech_output_dict (dict): Dictionary with keys (location, interval, tech) and values as original sizes
        cc_fraction_dict (dict): Dictionary with keys (location, interval, tech) and values as CC fractions
        capture_rate (float): Maximum possible capture rate for normalization

    Returns:
        dict: Updated dictionary with new CC technology entries and adjusted non-CC values
    """
    print("The technologies dictionary will be splitted to carbon capture and non carbon capture")

    updated_dict_cc = tech_output_dict.copy()

    for (location, interval, tech), cc_frac in cc_fraction_dict.items():
        if (location, interval, tech) not in tech_output_dict:
            print(f"No original size of {tech} in {tech_output_dict}")

        original_size = tech_output_dict[(location, interval, tech)]

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

# print(apply_cc_splitting(tech_output_dict, cc_fraction_dict, capture_rate))