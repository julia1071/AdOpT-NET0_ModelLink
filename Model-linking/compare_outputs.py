def compare_outputs(outputs_cluster, i, e):
    """
    Compare outputs from iteration i and i-1.
    Returns True if all relative differences are < e, else False.
    """

    if i <= 1:
        print("First iteration, skipping comparison.")
        return False  # Treat as pass to continue the loop

    prev = outputs_cluster[f"iteration_{i - 1}"]
    curr = outputs_cluster[f"iteration_{i}"]

    # Compare all technologies that appear in either iteration
    all_techs = set(prev.keys()).union(set(curr.keys()))

    for tech in all_techs:
        prev_years = prev.get(tech, {})
        curr_years = curr.get(tech, {})

        all_years = set(prev_years.keys()).union(set(curr_years.keys()))

        for year in all_years:
            val_prev = prev_years.get(year, 0)
            val_curr = curr_years.get(year, 0)

            if val_prev == 0 and val_curr != 0:
                print(f"{tech} was not selected in the previous iteration but has value {val_curr} in {year}")
                return False

            if val_prev != 0 and val_curr == 0:
                print(f"{tech} had value {val_prev} in {year} in previous iteration but is not selected now")
                return False

            if val_prev != 0:
                relative_diff = abs((val_curr - val_prev) / val_prev)
                if relative_diff > e:
                    print(f"Relative difference too large for {tech} in {year}: {relative_diff:.4f} > {e}")
                    return False

    print(f"✅ All changes between iteration {i - 1} and {i} are within threshold {e}")
    return True

