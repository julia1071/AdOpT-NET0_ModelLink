import config_model_linking as cfg
from adopt_net0.utilities import get_set_t


def extract_and_apply_import_bio_ratios(adopt_hub, tech_output_dict):
    """
    Extracts the bio carrier import ratios per interval and applies them to split
    selected technologies into bio and non-bio variants.

    Args:
        adopt_hub: Model results object.
        tech_output_dict (dict): {(location, interval, tech): size}

    Returns:
        dict: Updated dictionary with '_bio' and non-bio versions of relevant technologies.
    """

    print("🔍 Extracting bio import ratios and splitting technologies")

    resolution = 'full' if cfg.fast_run else 'clustered'
    updated_dict = tech_output_dict.copy()
    bio_ratios = {}

    for interval in cfg.intervals:
        interval_block = adopt_hub[interval].model[resolution].periods[interval]
        set_t = get_set_t(adopt_hub[interval].data.model_config, interval_block)
        node_block = interval_block.node_blocks[cfg.location]

        total_bio = total_fossil = 0.0

        for carrier in cfg.bio_carriers:
            bio_carrier = f"bio_{carrier}"

            # Sum bio and fossil import flows across all timesteps
            bio_val = sum(node_block.var_import_flow[t, bio_carrier].value or 0 for t in set_t)
            foss_val = sum(node_block.var_import_flow[t, carrier].value or 0 for t in set_t)

            total_bio += bio_val
            total_fossil += foss_val

        total = total_bio + total_fossil
        ratio = total_bio / total if total > 0 else 0.0
        bio_ratios[(cfg.location, interval)] = ratio

        print(f"📦 Interval '{interval}': bio import ratio = {ratio:.2%}")

    print("🔀 Splitting technologies in cfg.bio_tech_names into bio and non-bio")

    for (loc, interval, tech) in list(tech_output_dict):
        if tech not in cfg.bio_tech_names:
            continue

        original_size = tech_output_dict[(loc, interval, tech)]
        bio_ratio = bio_ratios.get((loc, interval), 0.0)

        if bio_ratio > 0:
            bio_size = original_size * bio_ratio
            non_bio_size = original_size * (1 - bio_ratio)

            updated_dict[(loc, interval, f"{tech}_bio")] = bio_size
            updated_dict[(loc, interval, tech)] = non_bio_size  # overwrite

    return updated_dict

