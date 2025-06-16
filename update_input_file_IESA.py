# pip install xlwings
import xlwings as xw
import shutil

def update_input_file_IESA(template_path,output_path, sheet_name, tech_id_col, tech_id_row_start, merged_row, header_row, merged_name, update_data):
    print("Update the input file of IESA")

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

    # Expand update_data to fill intermediate years (e.g., 2035 and 2045)
    expanded_update_data = {}

    for tech_id, year_vals in update_data.items():
        expanded_year_vals = {}
        sorted_years = sorted(year_vals.keys())
        for year in sorted_years:
            expanded_year_vals[year] = year_vals[year]  # Keep original
            if year == 2030 and 2035 not in year_vals:
                expanded_year_vals[2035] = year_vals[year]
            if year == 2040 and 2045 not in year_vals:
                expanded_year_vals[2045] = year_vals[year]
        expanded_update_data[tech_id] = expanded_year_vals

    # Step 6: Write values
    for tech_id, year_vals in expanded_update_data.items():
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
