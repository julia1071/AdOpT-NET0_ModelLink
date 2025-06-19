def compare_outputs(outputs_cluster, i, e):
    """
    Compare outputs from iteration i and i-1.
    Skips comparison if i == 1.
    Returns True if all relative differences are < e, else False.
    """
    if i <= 1:
        print("First iteration, skipping comparison.")
        return False  # Treat as pass to continue the loop

    prev = outputs_cluster[i - 1]
    curr = outputs_cluster[i]

    for tech in curr:
        if tech not in prev:
            print(f"New tech in iteration {i}: {tech}")
            return False

        for year in curr[tech]:
            val_prev = prev[tech].get(year, 0)
            val_curr = curr[tech].get(year, 0)

            if val_prev == 0 and val_curr != 0:
                print(f"Value for {tech} in {year} changed from 0 to {val_curr}")
                return False

            if val_prev != 0:
                relative_diff = abs((val_curr - val_prev) / val_prev)
                if relative_diff > e:
                    print(f"Relative difference too large for {tech} in {year}: {relative_diff:.4f} > {e}")
                    return False

    print(f"All changes between iteration {i-1} and {i} are within threshold {e}")
    return True
