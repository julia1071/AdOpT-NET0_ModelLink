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
    updated_dict = {cat: vals.copy() for cat, vals in tech_output_dict.items()}
    bio_ratios = {}

    for interval in cfg.intervals:
        interval_block = adopt_hub[interval].model[resolution].periods[interval]
        set_t = get_set_t(adopt_hub[interval].data.model_config, interval_block)
        node_block = interval_block.node_blocks[cfg.location]

        total_bio = total_fossil = 0.0

        for carrier in cfg.bio_carriers:
            bio_carrier = f"{carrier}_bio"

            # Sum bio and fossil import flows across all timesteps
            bio_val = sum(node_block.var_import_flow[t, bio_carrier].value for t in set_t) if any(car == bio_carrier for (_, car) in node_block.var_import_flow.index_set()) else 0
            foss_val = sum(node_block.var_import_flow[t, carrier].value for t in set_t) if any(car == carrier for (_, car) in node_block.var_import_flow.index_set()) else 0

            total_bio += bio_val
            total_fossil += foss_val

            total = total_bio + total_fossil
            ratio = total_bio / total if total > 0 else 0.0
            bio_ratios[(cfg.location, interval, carrier)] = ratio

            print(f"📦 Interval '{interval}': {bio_carrier} import ratio = {ratio:.2%}")

    print("🔀 Splitting technologies in cfg.bio_tech_names into bio and non-bio")

    for category, subdict in tech_output_dict.items():
        for (loc, interval, tech) in list(subdict):
            if tech not in cfg.bio_tech_names:
                continue

            original_size = subdict[(loc, interval, tech)]

            for carrier in cfg.bio_carriers:
                bio_ratio = bio_ratios.get((loc, interval, carrier), 0.0)

                if bio_ratio > 0:
                    bio_size = original_size * bio_ratio
                    non_bio_size = original_size * (1 - bio_ratio)

                    updated_dict[category][(loc, interval, f"{tech}_bio")] = bio_size
                    updated_dict[category][(loc, interval, tech)] = non_bio_size

    return updated_dict

