from adopt_net0.utilities import get_set_t
import config_model_linking as cfg

def extract_and_apply_cc_fractions(adopt_hub, tech_output_dict):
    """
    Extracts carbon capture (CC) fractions for selected technologies from HDF5 results.
    Includes "_existing" variants automatically.

    Args:
        adopt_hub: The model object with the results of the cluster.
        tech_output_dict (dict): {(location, interval, tech): size}

    Returns:
        dict: updated technology dictionary with separated CC and non-CC variants
    """
    print("Extracting CC fractions for selected technologies (including _existing variants)")

    resolution = 'full' if cfg.fast_run else 'clustered'

    # Extend CC technologies to include "_existing" variants
    cc_tech_map = {
        alias_variant: tech_variant
        for alias, base_tech in cfg.cc_technologies.items()
        for alias_variant, tech_variant in [
            (alias, base_tech),
            (f"{alias}_existing", f"{base_tech}_existing"),
        ]
    }

    def safe_sum(var_dict, keys):
        return sum(var_dict[k].value or 0 for k in keys if var_dict[k].value is not None)

    def get_cc_tech_name(tech):
        return tech.replace("_existing", "_CC_existing") if tech.endswith("_existing") else f"{tech}_CC"

    cc_fraction_dict = {}

    for interval in cfg.intervals:
        interval_block = adopt_hub[interval].model[resolution].periods[interval]
        set_t = get_set_t(adopt_hub[interval].data.model_config, interval_block)
        node_block = interval_block.node_blocks[cfg.location]
        tech_blocks = node_block.tech_blocks_active

        for alias, tech_name in cc_tech_map.items():
            if tech_name not in tech_blocks:
                continue

            tech_block = tech_blocks[tech_name]
            CO2_captured = safe_sum(tech_block.var_output_ccs, [(t, 'CO2captured') for t in set_t])
            total_emission = safe_sum(tech_block.var_tec_emissions_pos, set_t)

            numerator = CO2_captured
            denominator = CO2_captured + total_emission

            if denominator > 1 and numerator > 1:
                frac_CC = numerator / denominator
                cc_fraction_dict[(cfg.location, interval, alias)] = frac_CC


    # Filter out entries with zero CC fraction
    cc_fraction_dict = {
        key: value for key, value in cc_fraction_dict.items() if value > 0
    }

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
                f"➡️ Check if the correct 'output_var_name' is defined in base_tech_output_map."
            )

        original_size = tech_output_dict[key]
        cc_ratio = min(cc_frac / cfg.capture_rate, 1.0)
        non_cc_ratio = 1 - cc_ratio

        size_cc = original_size * cc_ratio
        size_non_cc = original_size * non_cc_ratio

        updated_dict_cc[(location, interval, get_cc_tech_name(tech))] = size_cc
        updated_dict_cc[key] = size_non_cc

    return updated_dict_cc

