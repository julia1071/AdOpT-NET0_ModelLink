from conversion_factors import conversion_factor_cluster_to_IESA


def map_techs_to_ID(updated_dict_bio, tech_to_id):
    """
    Maps technology names to technology IDs, supports one-to-many mappings,
    applies tech-specific unit conversion, and returns only non-zero values per Tech_ID.

    Args:
        updated_dict_bio (dict): {(location, year, tech_name): value}
        tech_to_id (dict): {tech_name: tech_id or list of tech_ids}

    Returns:
        dict: {tech_id: {year: converted_value}}, only for non-zero values
    """
    print("The technologies are mapped based on their corresponding Tech_ID and conversion factor.")
    updates = {}

    # Collect all years seen in the input
    all_years = sorted({int(year) for (_, year, _) in updated_dict_bio.keys()})

    # Process input values and apply conversion
    for (loc, year, tech), value in updated_dict_bio.items():
        tech_ids = tech_to_id.get(tech)
        if tech_ids is None:
            continue  # Tech not mapped

        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            try:
                conversion = conversion_factor_cluster_to_IESA(tech_id)
            except ValueError as e:
                print(e)
                continue

            scaled_value = float(value) * conversion
            if scaled_value == 0.0:
                continue  # Skip storing zeroes

            if tech_id not in updates:
                updates[tech_id] = {}
            updates[tech_id][int(year)] = scaled_value

    return updates


