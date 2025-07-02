# cc_fraction_dict = {('Zeeland', '2040', 'MPW2methanol_input'): 0.890088621056363}
# tech_output_dict = {('Zeeland', '2030', 'CrackerFurnace'): 2516727.272727268, ('Zeeland', '2030', 'PDH'): 612970.0727272722, ('Zeeland', '2030', 'AEC'): 4676430.279057744, ('Zeeland', '2030', 'ElectricSMR_m'): 365977.9107377938, ('Zeeland', '2040', 'MTO'): 205491.35776519336, ('Zeeland', '2040', 'PDH_existing'): 292950.1831695437, ('Zeeland', '2040', 'MPW2methanol_input'): 857607.6030432511, ('Zeeland', '2040', 'MPW2methanol_output'): 1260683.176473579, ('Zeeland', '2040', 'ElectricSMR_m'): 999788.7071749736, ('Zeeland', '2040', 'ElectricSMR_m_existing'): 359669.7690299599, ('Zeeland', '2040', 'CO2electrolysis'): 1010855.7349471111, ('Zeeland', '2050', 'PDH_existing'): 343486.9999999993, ('Zeeland', '2050', 'AEC_existing'): 3931274.7043490848, ('Zeeland', '2050', 'ElectricSMR_m_existing'): 556320.2905021796, ('Zeeland', '2050', 'CO2electrolysis'): 332427.648207849, ('Zeeland', '2050', 'CO2electrolysis_existing'): 1041395.3517921506}
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
    print("The technologies dictionary will be split into carbon capture and non-carbon capture")

    updated_dict_cc = tech_output_dict.copy()

    for (location, interval, tech), cc_frac in cc_fraction_dict.items():
        key = (location, interval, tech)
        if key not in tech_output_dict:
            raise ValueError(
                f"❌ Inconsistent data detected:\n"
                f" - Technology: '{tech}'\n"
                f" - Interval: '{interval}'\n"
                f" - Location: '{location}'\n"
                f"A carbon capture fraction was found, but the technology's output value is missing.\n"
                f"CO₂ emissions were extracted, implying the technology was active — "
                f"but the technology’s main output (as defined in base_tech_output_map) was not found in the HDF5.\n"
                f"➡️ Please check if the correct 'output_var_name' was used for this technology."
            )

        original_size = tech_output_dict[key]

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
        updated_dict_cc[key] = size_non_cc  # overwrite

    return updated_dict_cc


# print(apply_cc_splitting(tech_output_dict, cc_fraction_dict, capture_rate))