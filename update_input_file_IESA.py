# pip install xlwings
import xlwings as xw
import shutil

# Excel must be installed on the server.
# This method is used because the "complicated" Excel input file for IESA-Opt gets corrupted while using openpyxl.

template_path = "U:/IESA-Opt-ModelLinking/data/20250430_detailed - kopie.xlsx" #Create a template (base) input file.
output_path = "U:/IESA-Opt-ModelLinking/data/20250430_detailed.xlsx" #Save the file with a name that is corresponding to the name defined in runDataReading AIMMS

def update_multiple_techs_and_years(
        template_path: str,
        output_path: str,
        sheet_name: str,
        tech_id_col: str,
        tech_id_row_start: int,
        merged_row: int,
        header_row: int,
        merged_name: str,
        update_data: dict
):
    # Step 1: Copy the clean template to the target output path
    shutil.copy(template_path, output_path)

    # Step 2: Open the copied workbook
    app = xw.App(visible=False)
    wb = xw.Book(output_path)
    ws = wb.sheets[sheet_name]

    # Step 3: Find the merged column range with the specified header
    merged_range = None
    last_col = ws.used_range.last_cell.column

    for cell in ws.range((merged_row, 1), (merged_row, last_col)):
        if cell.merge_cells and isinstance(cell.value, str):
            if merged_name.strip().lower() == cell.value.strip().lower():
                merged_range = cell.merge_area
                break

    if not merged_range:
        wb.close()
        app.quit()
        return f"❌ Merged header '{merged_name}' not found."

    # Step 4: Build mapping of year → column index
    year_to_column = {}
    for col in range(merged_range.column, merged_range.last_cell.column + 1):
        cell = ws.range((header_row, col))
        val = cell.value
        try:
            year = int(float(str(val).strip()))
            year_to_column[year] = col
        except (ValueError, TypeError):
            continue

    print("✅ Found years:", list(year_to_column.keys()))

    # Step 5: Build mapping of Tech_ID → row
    tech_id_to_row = {}
    row = tech_id_row_start
    while True:
        tech_cell = ws.range(f"{tech_id_col}{row}")
        tech_id = tech_cell.value
        if tech_id is None:
            break
        tech_id_to_row[str(tech_id).strip()] = row
        row += 1

    # Step 6: Write values
    for tech_id, year_vals in update_data.items():
        if tech_id not in tech_id_to_row:
            print(f"⚠️ Skipping missing Tech_ID: {tech_id}")
            continue
        for year, val in year_vals.items():
            col = year_to_column.get(year)
            if col is None:
                print(f"⚠️ Skipping year {year} for Tech_ID {tech_id} (not found)")
                continue
            row = tech_id_to_row[tech_id]
            print(f"✍️ Writing {val} to row {row}, col {col} (Tech_ID={tech_id}, Year={year})")
            ws.range((row, col)).value = val

    # Step 7: Save and close workbook
    wb.save()
    wb.close()
    app.quit()
    return "✅ All values written successfully."



#Example to check what the code does.
updates = {
    "Res01_01": {2030: 0, 2050: 0},
    "Res01_02": {2030: 0, 2050: 0},
    "Res02_01": {2030: 0, 2050: 0}
}

result = update_multiple_techs_and_years(
    template_path=template_path,
    output_path=output_path,
    sheet_name="Technologies",
    tech_id_col="A",
    tech_id_row_start=7,
    merged_row=2,
    header_row=5,
    merged_name="Minimum use in a year",
    update_data=updates
)

print(result)