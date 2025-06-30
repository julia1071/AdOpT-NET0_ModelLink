import pandas as pd
# from pathlib import Path
# file_path = Path("U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/Results_model_linking_simplified_20250627_17_36/ResultsModelLinking_General_Iteration_1.xlsx")


def calculate_avg_bio_methane_cost(file_path, year):
    """
    Calculates the weighted average cost of bio-methane production based on LCOE components
    and technology outputs for a given year. Provides a summary of found and missing data.

    Args:
        file_path (str or Path): Path to the Excel file containing IESA output data
        year (str): The target year to extract values for

    Returns:
        float or None: The weighted average cost, or None if no output is found
    """

    technologies = ["Gas04_01", "Gas04_02", "Gas04_03", "Gas04_04"]
    components = ["CAPEX", "FOM", "VOC", "Fuels"]

    try:
        df_lcoe = pd.read_excel(file_path, sheet_name="LCOEs")
        df_sd = pd.read_excel(file_path, sheet_name="SupplyDemand")
    except Exception as e:
        raise ValueError(f"❌ Failed to load Excel sheets: {e}")

    # === Extract LCOE values ===
    costs = []
    found_costs = {}  # {tech: [found components]}
    for tech in technologies:
        total_cost = 0
        found_components = []
        for comp in components:
            mask = (
                (df_lcoe["Tech_ID"] == tech) &
                (df_lcoe["Type1"] == "Real") &
                (df_lcoe["Type2"] == comp)
            )
            row = df_lcoe[mask]
            try:
                val = float(row[year].values[0])
                total_cost += val
                found_components.append(comp)
            except (IndexError, KeyError, ValueError):
                pass  # missing component is allowed
        if found_components:
            found_costs[tech] = found_components
        costs.append((tech, total_cost))

    # === Extract output values ===
    outputs = []
    found_outputs = []
    for tech in technologies:
        mask = (
            (df_sd["Type"] == "supply") &
            (df_sd["Tech_ID"] == tech)
        )
        row = df_sd[mask]
        try:
            output = float(row[year].values[0])
            found_outputs.append(tech)
        except (IndexError, KeyError, ValueError):
            output = 0
        outputs.append((tech, output))

    # === Summary: what was found ===
    print("\n📊 Bio-methane cost component summary:")
    if found_costs:
        for tech, comps in found_costs.items():
            print(f" - {tech}: found components → {', '.join(comps)}")
    else:
        print("⚠️ No cost components found for any bio-methane technologies.")

    print("\n📦 Bio-methane output summary:")
    if found_outputs:
        print(f"Found outputs for: {', '.join(found_outputs)}")
    else:
        print("⚠️ No outputs found for any bio-methane technologies.")

    # === Weighted average cost calculation ===
    weighted_sum = sum(c * o for (t1, c), (t2, o) in zip(costs, outputs) if o)
    total_output = sum(o for _, o in outputs if o)

    avg_cost = weighted_sum / total_output if total_output > 0 else None

    return avg_cost

# print(calculate_avg_bio_methane_cost(file_path, '2025'))


