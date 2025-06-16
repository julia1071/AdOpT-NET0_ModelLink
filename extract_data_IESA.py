import pandas as pd
import sys

# Function to extract data by looping through the years and sheets
def extract_data_IESA (intervals, list_sheets, nrows, filters, headers,file_path):
    print("Start extracting data from IESA-Opt")
    if len(list_sheets) != len(nrows) or len(list_sheets) != len(headers) or len(list_sheets) != len(filters):
        print("Error: The indices of number of rows, headers or filters does not match the number of sheets.")
        sys.exit()

    results_year_sheet= {} # Create an empty dictionary with a list for each year

    for interval in intervals:
        for sheet in list_sheets:
            results_year_sheet[f"results_{interval}_{sheet}"] = []

    for i in range(len(intervals)):
        for j in range(len(list_sheets)):

            # Read the DataFrame for the different Excel sheets from which results are extracted.
                df = pd.read_excel(file_path, sheet_name=list_sheets[j], nrows= nrows[j], header=0)
                for k in range(len(filters[j])):

                    # Filter the rows by activity (e.g., 'Naphtha', 'Bio Naphtha', etc.)
                    row = df[df[headers[j]] == filters[j][k]]

                    if not row.empty:
                        # If the row is not empty, get the corresponding value for the year
                        value = float(row[intervals[i]].values[0])
                    else:
                        # If the row is empty, print a message (or you could assign None)
                        value = None
                        print(f"Row was empty for '{headers[j]}' '{filters[j][k]}' in year '{intervals[i]}'")

                    # Append the result to the dictionary for the corresponding year-sheet combination
                    results_year_sheet[f"results_{intervals[i]}_{list_sheets[j]}"].append({
                        "filter": filters[j][k],
                        "value": value
                    })

    #Return the final results dictionary
    print("The raw results dictionary from IESA-Opt is created")
    return results_year_sheet

#results= extract_data_IESA(intervals,list_sheets,nrows,filters,headers,file_path)
#print(results)

#Get specific values from created dictionary
def get_value_IESA(results_year_sheet,interval, sheet, filter):
    key = f"results_{interval}_{sheet}"
    entries = results_year_sheet.get(key, [])
    for entry in entries:
        if entry['filter'] == filter:
            return entry['value']
    raise ValueError(f"No value is found for {interval}, {sheet}, {filter}")

#value_2030_X= get_value_IESA(results, '2030','Configuration_Stock', filter_stock[1])
#print(value_2030_X)