import pandas as pd
import sys
from pathlib import Path

def extract_data_IESA_multiple(intervals, list_sheets, nrows, filters, headers, file_path):
    print("Start extracting data from IESA-Opt (with named filters)")

    if len(list_sheets) != len(nrows) or len(list_sheets) != len(headers) or len(list_sheets) != len(filters):
        print("Error: The number of sheets, headers, filters, or nrows do not match.")
        sys.exit()

    results_year_sheet = {}

    for interval in intervals:
        for sheet in list_sheets:
            results_year_sheet[f"results_{interval}_{sheet}"] = []

    for i in range(len(intervals)):
        for j in range(len(list_sheets)):
            df = pd.read_excel(file_path, sheet_name=list_sheets[j], nrows=nrows[j], header=0)

            header = headers[j]
            sheet_filters = filters[j]

            for filter_values in sheet_filters:
                if isinstance(header, str):
                    # Single-header case
                    row = df[df[header] == filter_values]
                    filter_entry = {header: filter_values}
                elif isinstance(header, tuple) and isinstance(filter_values, tuple):
                    # Multi-header case (2 or more)
                    condition = pd.Series([True] * len(df))
                    filter_entry = {}
                    for h, f in zip(header, filter_values):
                        condition &= df[h] == f
                        filter_entry[h] = f
                    row = df[condition]
                else:
                    raise ValueError(f"Header/filter mismatch in sheet {list_sheets[j]}")

                if not row.empty:
                    value = float(row[intervals[i]].values[0])
                else:
                    value = None
                    print(f"Row was empty for filters {filter_entry} in year '{intervals[i]}'")

                filter_entry["value"] = value
                results_year_sheet[f"results_{intervals[i]}_{list_sheets[j]}"].append(filter_entry)

    print("The raw results dictionary from IESA-Opt is created")
    return results_year_sheet


# intervals = ['2030', '2040', '2050']
# file_path = Path("U:/IESA-Opt-Dev_20250605_linking_correct/Output/ResultsModelLinking/Results_model_linking_20250621_09_08/ResultsModelLinking_General_Iteration_1.xlsx")
#
# list_sheets = ["LCOEs", "SupplyDemand"]
# headers = [("Tech_ID", "Type1", "Type2"), ("Type", "Tech_ID")]
# filters = [
#     [ ("TNB01_01", "Real","Fuels"), ("TNB01_03", "Real","Fuels") ],
#     [("supply", "WAI01_01"), ("supply", "WAI01_02")]
# ]
# nrows = [1689, 830]
#
# results = extract_data_IESA_multiple(intervals, list_sheets, nrows, filters, headers, file_path)
# print(results)

def get_value_IESA_multiple(results_year_sheet, interval, sheet, **filters):
    key = f"results_{interval}_{sheet}"
    entries = results_year_sheet.get(key, [])

    for entry in entries:
        if all(entry.get(k) == v for k, v in filters.items()):
            return entry['value']

    raise ValueError(f"No value found for {interval}, {sheet}, filters: {filters}")

# x = get_value_IESA_multiple(
#     results, 2030, "LCOEs",
#     Tech_ID="TNB01_01", Type1="Real", Type2="Fuels"
# )
#
# y = get_value_IESA_multiple(
#     results, 2040, "SupplyDemand",
#     Type="supply", Tech_ID="WAI01_02"
# )
# print(x,y)