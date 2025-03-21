import pandas as pd

# Load the Excel file
file_path = "C:/EHubversions/AdOpT-NET0_Julia/Plotting/result_data_long.xlsx"  # Update with the correct path if needed
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Define the filter criteria
keywords = ["size_", "electricity/import_max", "CO2/export_max",
            "methane/import_max", "methane_bio/import_max", "CO2_DAC/import_max"]

# Filter the DataFrame
first_column_name = df.columns[0]
filtered_df = df[df[first_column_name].astype(str).str.startswith(tuple(keywords))]

# Save the filtered data back to an Excel file
filtered_excel_path = "C:/EHubversions/AdOpT-NET0_Julia/Plotting/filtered_data.xlsx"
filtered_df.to_excel(filtered_excel_path, index=False)

# Convert the filtered DataFrame to a LaTeX table
latex_table = filtered_df.to_latex(index=False, escape=False)

# Save the LaTeX table to a file
latex_file_path = "C:/EHubversions/AdOpT-NET0_Julia/Plotting/filtered_data.tex"
with open(latex_file_path, "w") as f:
    f.write(latex_table)

print(f"Filtered data saved to: {filtered_excel_path}")
print(f"LaTeX table saved to: {latex_file_path}")
