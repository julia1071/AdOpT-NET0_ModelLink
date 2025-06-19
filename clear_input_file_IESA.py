import xlwings as xw


def clear_input_file_IESA(input_path, sheet_name, tech_id_col, tech_id_row_start, merged_row, header_row, merged_name, tech_to_id):
    print("🧹 Clearing all relevant values from IESA input file...")

    app = xw.App(visible=False)
    wb = xw.Book(input_path)
    ws = wb.sheets[sheet_name]

    # Step 1: Find merged header area
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
        print(f"❌ Merged header '{merged_name}' not found.")
        return

    # Step 2: Map years to columns
    year_to_column = {}
    for col in range(merged_range.column, merged_range.last_cell.column + 1):
        val = ws.range((header_row, col)).value
        try:
            year = int(float(str(val).strip()))
            year_to_column[year] = col
        except (ValueError, TypeError):
            continue

    # Add interpolated years
    all_years = set(year_to_column.keys())
    if 2030 in all_years:
        all_years.add(2035)
    if 2040 in all_years:
        all_years.add(2045)

    # Step 3: Map Tech_IDs to rows
    tech_id_to_row = {}
    row = tech_id_row_start
    while True:
        tech_cell = ws.range(f"{tech_id_col}{row}")
        tech_id = tech_cell.value
        if tech_id is None:
            break
        tech_id_to_row[str(tech_id).strip()] = row
        row += 1

    # Step 4: Clear all matching cells
    for tech_id in tech_to_id.values():
        row = tech_id_to_row.get(tech_id)
        if row is None:
            continue
        for year in all_years:
            col = year_to_column.get(year)
            if col:
                ws.range((row, col)).clear_contents()

    wb.save()
    wb.close()
    app.quit()
    print("✅ IESA input file cleaned successfully.")

# tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03",
#                   "CrackerFurnace_Electric": "ICH01_05",
#                   "CrackerFurnace_Electric_bio": "ICH01_06", "EDH": "ICH01_11", "MTO": "ICH01_12", "PDH": "ICH01_14",
#                   "MPW2methanol": "RFS04_01",
#                   "DirectMeOHsynthesis": "RFS04_02", "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
#                   "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
#                   }
#
# input_path = "U:/IESA-Opt-Dev_20250605_linking_correct/data/20250612_detailed_linked_test (1).xlsx"  # Save the file with a name that is corresponding to the name defined in runDataReading AIMMS
#
# clear_input_file_IESA(
#     input_path,
#     sheet_name="Technologies",
#     tech_id_col="A",
#     tech_id_row_start=7,
#     merged_row=2,
#     header_row=5,
#     merged_name="Minimum use in a year",
#     tech_to_id=tech_to_id
# )
