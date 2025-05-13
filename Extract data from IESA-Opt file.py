import pandas as pd
import sys

# Replace 'your_file.xlsx' with the path to your Excel file
file_path = "U:/IESA-Opt_latestversion/Output/2025-05-07_17.30/2025-05-07_17.30_General.xlsx"

#Define simulation years cluster model and the excel sheets from which you want to extract data in IESA-Opt
simulation_years=['2030','2040','2050']
list_sheets= ['EnergyCosts','Configuration_Stock']
nrows=[40, 320]#!Same order as list_sheets! =Number of rows in excel sheet -1

#Define the corresponding properties of the sheets and the specific data that you want to extract .
header_energycosts = 'Activity'
filter_energycosts = ['Naphtha', 'Bio Naphtha', 'Bio Ethanol', 'Electricity EU', 'Sugars', 'Manure']

header_stock = 'Tech_ID'
filter_stock = ['RFP02_01', 'WAI01_03']

#!Combine the headers and filters of the different sheets! Same order as list_sheets!
headers = [header_energycosts,header_stock]
filters= [filter_energycosts, filter_stock]

# Function to extract data by looping through the years and sheets
def extract_data_iesa_opt(simulation_years, list_sheets, nrows, filters, headers):
    if len(list_sheets) != len(nrows) or len(list_sheets) != len(headers) or len(list_sheets) != len(filters):
        print("Error: The number of rows (nrows) does not match the number of sheets.")
        sys.exit()
    results_year_sheet= {} # Create an empty dictionary with a list for each year
    for year in simulation_years:
        for sheet in list_sheets:
            results_year_sheet[f"results_{year}_{sheet}"] = []
    for i in range(len(simulation_years)):
        for j in range(len(list_sheets)):
            # Read the DataFrame for the 'Energy Costs' sheet
                df = pd.read_excel(file_path, sheet_name=list_sheets[j], nrows= nrows[j], header=0)
                for k in range(len(filters[j])):
                    # Filter the rows by activity (e.g., 'Naphtha', 'Bio Naphtha', etc.)
                    row = df[df[headers[j]] == filters[j][k]]

                    if not row.empty:
                        # If the row is not empty, get the corresponding value for the year
                        value = float(row[simulation_years[i]].values[0])
                    else:
                        # If the row is empty, print a message (or you could assign None)
                        value = None
                        print(f"Row was empty for activity '{filters[j][k]}' in year '{simulation_years[i]}'")

                    # Append the result to the dictionary for the corresponding year-sheet combination
                    results_year_sheet[f"results_{simulation_years[i]}_{list_sheets[j]}"].append({
                        "filter": filters[j][k],
                        "value": value
                    })

    #Return the final results dictionary
    return results_year_sheet

results= extract_data_iesa_opt(simulation_years,list_sheets,nrows,filters,headers)
print(results)

#Get specific values from created dictionary
def get_specific_value(results_IESA,year, sheet, filter):
    key = f"results_{year}_{sheet}"
    entries = results_IESA.get(key, [])
    for entry in entries:
        if entry['filter'] == filter:
            return entry['value']
    raise ValueError(f"No value is found for {year}, {sheet}, {filter}")

value_2030_X= get_specific_value(results, '2030','Configuration_Stock', filter_stock[1])
print(value_2030_X)