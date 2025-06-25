from extract_data_IESA_multiple_headers import extract_data_IESA_multiple, get_value_IESA_multiple
from pathlib import Path

file_path = Path("U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/Results_model_linking_20250621_09_08/ResultsModelLinking_General_Iteration_1.xlsx")


def calculate_avg_bio_methane_cost(file_path, year):
    # Define the relevant technologies and cost components
    technologies = ["Gas04_01", "Gas04_02", "Gas04_03", "Gas04_04"]
    components = ["CAPEX", "FOM", "VOC", "Fuels"]

    # === LCOEs Sheet ===
    lcoe_header = ("Tech_ID", "Type1", "Type2")
    lcoe_filters = [(tech, "Real", comp) for tech in technologies for comp in components]

    # === SupplyDemand Sheet ===
    supplydemand_header = ("Type", "Tech_ID")
    supplydemand_filters = [("supply", tech) for tech in technologies]

    # === Assemble inputs for extract_data_IESA_multiple ===
    list_sheets = ["LCOEs", "SupplyDemand"]
    headers = [lcoe_header, supplydemand_header]
    filters = [lcoe_filters, supplydemand_filters]
    nrows = [1689, 830]  # Adjust based on your Excel file

    # === Now ready to pass into your extract function ===
    results = extract_data_IESA_multiple(
        intervals=["2025", "2030", "2040"],
        list_sheets=list_sheets,
        nrows=nrows,
        filters=filters,
        headers=headers,
        file_path=file_path
    )
    costs = []
    for tech in technologies:
        total_cost = 0
        for comp in components:
            try:
                val = get_value_IESA_multiple(results, year, "LCOEs", Tech_ID=tech, Type1="Real", Type2=comp)
                if val is not None:
                    total_cost += val
            except ValueError:
                print(f"Missing LCOE value for {tech} - {comp}")
        costs.append((tech, total_cost))  # Store cost per PJ

    outputs = []
    for tech in technologies:
        try:
            output = get_value_IESA_multiple(results, year, "SupplyDemand", Type="supply", Tech_ID=tech)
        except ValueError:
            output = 0
            print(f"Missing output for {tech}")
        outputs.append((tech, output))  # PJ of output

    weighted_sum = sum(c * o for (t1, c), (t2, o) in zip(costs, outputs) if o is not None)
    total_output = sum(o for _, o in outputs if o is not None)

    avg_cost = weighted_sum / total_output if total_output > 0 else None
    return avg_cost

print(calculate_avg_bio_methane_cost(results, 2025))