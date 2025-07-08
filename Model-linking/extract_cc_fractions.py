from adopt_net0.utilities import get_set_t
import config_model_linking as cfg

def extract_and_apply_cc_fractions(adopt_hub, tech_output_dict):
    """
    Extracts carbon capture (CC) fractions for specified technologies from HDF5 result files
    in the cluster model output. Also includes _existing variants automatically.

    Args:
        adopt_hub: The model object with the results of the cluster.
        tech_output_dict (dict): Dictionary with technology sizes from the cluster model

    Returns:
        dict: {(location, interval, tech_alias): cc_fraction} with floats between 0 and 1
    """
    print("Extracting CC fractions for selected technologies (including _existing variants)")

    # Step 1: Extend cc_technologies to include _existing variants
    cc_tech_map = {}
    for alias, base_tech in cfg.cc_technologies.items():
        cc_tech_map[alias] = base_tech
        cc_tech_map[f"{alias}_existing"] = f"{base_tech}_existing"

    # Define scaling factor if using fast_run
    resolution = 'full' if cfg.fast_run else 'clustered'

    cc_fraction_dict = {}

    for interval in cfg.intervals:
        interval_block = adopt_hub[interval].model[resolution].periods[interval]
        set_t = get_set_t(adopt_hub[interval].data.model_config, interval_block)
        for alias, tech_name in cc_tech_map.items():
            if tech_name in interval_block.node_blocks[cfg.location].tech_blocks_active:
                tech_block = interval_block.node_blocks[cfg.location].tech_blocks_active[tech_name]

                CO2_captured = sum(tech_block.var_output_ccs[t, 'CO2captured'].value for t in set_t)
                total_emission = sum(tech_block.var_tec_emissions_pos[t].value for t in set_t)

                numerator = CO2_captured
                denominator = CO2_captured + total_emission
                frac_CC = numerator / denominator if (denominator > 1 and numerator > 1) else 0

                cc_fraction_dict[(cfg.location, interval, alias)] = float(frac_CC)

    # Filter out entries with zero CC fraction
    cc_fraction_dict = {
        key: value for key, value in cc_fraction_dict.items() if value > 0
    }

    print("The technologies dictionary will be split into carbon capture and non-carbon capture")

    updated_dict_cc = tech_output_dict.copy()

    for (interval, tech), cc_frac in cc_fraction_dict.items():
        key = (cfg.location, interval, tech)
        if key not in tech_output_dict:
            raise ValueError(
                f"❌ Inconsistent data detected:\n"
                f" - Technology: '{tech}'\n"
                f" - Interval: '{interval}'\n"
                f" - Location: '{cfg.location}'\n"
                f"A carbon capture fraction was found, but the technology's output value is missing.\n"
                f"CO₂ emissions were extracted, implying the technology was active — "
                f"but the technology’s main output (as defined in base_tech_output_map) was not found in the HDF5.\n"
                f"➡️ Please check if the correct 'output_var_name' was used for this technology."
            )

        original_size = tech_output_dict[key]

        # Calculate shares
        cc_ratio = cc_frac / cfg.capture_rate
        non_cc_ratio = 1 - cc_ratio

        size_cc = original_size * cc_ratio
        size_non_cc = original_size * non_cc_ratio

        # Build new tech name (preserve "_existing" if present)
        if tech.endswith("_existing"):
            base_tech = tech.replace("_existing", "")
            cc_tech = f"{base_tech}_CC_existing"
        else:

            cc_tech = f"{tech}_CC"

        # Add to updated dictionary
        updated_dict_cc[(cfg.location, interval, cc_tech)] = size_cc
        updated_dict_cc[key] = size_non_cc  # overwrite

    return updated_dict_cc
