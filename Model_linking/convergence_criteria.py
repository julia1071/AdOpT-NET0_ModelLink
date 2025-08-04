import math

import config_model_linking as cfg

import numpy as np

def compare_cluster_outputs(epsilon, i, e):
    """
    Compares relative changes (epsilon) between iterations i and i-1.
    Returns True if convergence criteria are met, otherwise False.

    Args:
        epsilon (dict): {tech: {year: epsilon_value}}
        i (int): Current iteration index.
        e (float): Tolerance threshold for convergence.

    Returns:
        bool: True if convergence criteria met, False otherwise.
    """

    if i == 1:
        print("🌀 First iteration, skipping convergence check.")
        return False

    iter_key = f"iteration_{i}"
    if iter_key not in epsilon:
        print(f"⚠️ No epsilon data found for iteration {i}.")
        return False

    # Flatten all epsilon values into a list of floats
    epsilon_values = [
        val
        for tech_eps in epsilon[iter_key].values()
        for val in tech_eps.values()
    ]

    if not epsilon_values:
        print("⚠️ No valid epsilon values to compare.")
        return False

    # Convergence checks based on type
    if cfg.convergence_type == "All":
        converged = all(val < e for val in epsilon_values)

    elif cfg.convergence_type == "Average":
        converged = np.mean(epsilon_values) < e

    elif cfg.convergence_type == "Median":
        converged = np.median(epsilon_values) < e

    elif cfg.convergence_type == "Average_Max":
        converged = (np.mean(epsilon_values) < e) and all(val < cfg.e_max for val in epsilon_values)

    elif cfg.convergence_type == "Median_Max":
        converged = (np.median(epsilon_values) < e) and all(val < cfg.e_max for val in epsilon_values)

    else:
        raise ValueError(f"Unknown convergence type: {cfg.convergence_type}")

    if converged:
        print(f"✅ Converged at iteration {i} with type '{cfg.convergence_type}' — threshold {e}")
    else:
        print(
            f"❌ Not converged at iteration {i} — max ε = {max(epsilon_values):.4f}, avg = {np.mean(epsilon_values):.4f}")

    return converged



def get_cluster_epsilon(outputs_cluster, i):
    """
    Computes relative changes (epsilon) between two consecutive iterations
    of technology outputs for all technologies and years.

    Args:
        outputs_cluster (dict): Dictionary with keys like 'iteration_0', 'iteration_1', etc.,
                                each containing tech-year output data.
        i (int): Current iteration index.

    Returns:
        dict: Nested dictionary of {tech: {year: epsilon}} with relative changes.
    """

    prev = outputs_cluster[f"iteration_{i - 1}"]["AnnualOutput"]
    curr = outputs_cluster[f"iteration_{i}"]["AnnualOutput"]

    all_techs = set(prev.keys()).union(curr.keys())
    epsilon = {}

    for tech in all_techs:
        prev_years = prev.get(tech, {})
        curr_years = curr.get(tech, {})

        all_years = set(prev_years.keys()).union(curr_years.keys())
        epsilon[tech] = {}

        for year in all_years:
            val_prev = prev_years.get(year, 0)
            val_curr = curr_years.get(year, 0)

            if val_prev == 0:
                # If both are zero, change is zero; if only prev is zero, treat as inf or 1
                if val_curr == 0:
                    rel_change = 0.0
                else:
                    rel_change = float('inf')
            else:
                rel_change = abs((val_curr - val_prev) / val_prev)

            epsilon[tech][year] = rel_change

    return epsilon

