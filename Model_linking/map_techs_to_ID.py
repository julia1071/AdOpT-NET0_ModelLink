from conversion_factors import conversion_factor_cluster_to_IESA
import numpy as np

def map_techs_to_ID(tech_output_dict, tech_to_id):
    """
    Maps technology names to technology IDs, supports one-to-many mappings,
    applies tech-specific unit conversion, and returns only non-zero values per Tech_ID.

    Args:
        tech_output_dict (dict): {
            "AnnualOutput": {(location, year, tech_name): scalar_value},
            "Operation": {(location, year, tech_name): array/list of values}
        }
        tech_to_id (dict): {tech_name: tech_id or list of tech_ids}

    Returns:
        dict: {tech_id: {year: converted_value}}, only for non-zero values
              converted_value can be scalar or numpy array depending on category
    """
    print("The technologies are mapped based on their corresponding Tech_ID and conversion factor.")
    updates = {"AnnualOutput": {},
               "Operation": {}
               }

    for category, subdict in tech_output_dict.items():
        for (loc, year, tech), value in subdict.items():
            tech_ids = tech_to_id.get(tech)
            if tech_ids is None:
                print(f"Technology {tech} not mapped.")
                continue  # Tech not mapped

            if not isinstance(tech_ids, list):
                tech_ids = [tech_ids]

            # Convert lists to np.array for safe math operations
            if isinstance(value, list):
                value = np.array(value)

            for tech_id in tech_ids:
                if category == "AnnualOutput":
                    try:
                        conversion = conversion_factor_cluster_to_IESA(tech_id)
                    except ValueError as e:
                        print(e)
                        continue

                    # Multiply by conversion factor
                    if isinstance(value, np.ndarray):
                        scaled_value = value * conversion
                        # Skip if all zeros or all None (np.isnan)
                        if np.all((scaled_value == 0) | np.isnan(scaled_value)):
                            continue
                    else:
                        scaled_value = float(value) * conversion
                        if scaled_value == 0.0:
                            continue  # Skip storing zeroes
                elif category == "Operation":
                    scaled_value = value

                if tech_id not in updates[category]:
                    updates[category][tech_id] = {}

                # Store by year, replacing previous if exists (assumed last wins)
                updates[category][tech_id][int(year)] = scaled_value

    return updates




