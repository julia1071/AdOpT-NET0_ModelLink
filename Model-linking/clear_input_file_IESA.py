import xlwings as xw


def clear_input_file_IESA(input_path, sheet_name, tech_id_col, tech_id_row_start, merged_row, header_row, merged_name, tech_to_id):
    """
    Clears all input values in the specified Excel sheet related to the given Tech_IDs and years,
    based on a merged header. Supports both one-to-one and one-to-many tech_to_id mappings.

    Args:
        input_path (Path or str): Path to the Excel file.
        sheet_name (str): Name of the worksheet to clear.
        tech_id_col (str): Column letter where Tech_IDs are listed (e.g., "B").
        tech_id_row_start (int): First row where Tech_IDs start (below headers).
        merged_row (int): Row number of the merged category header (e.g., "Feedstocks").
        header_row (int): Row where year values are specified.
        merged_name (str): Name of the merged header block (e.g., "Feedstocks").
        tech_to_id (dict): Mapping from internal tech names to one or more IESA Tech_IDs.

    Returns:
        None
    """
    print("🧹 Clearing all relevant values from IESA input file...")

    app = xw.App(visible=False)
    wb = xw.Book(input_path)
    ws = wb.sheets[sheet_name]

    # Step 1: Locate the merged header area
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

    # Add interpolated years for compatibility with later write logic
    all_years = set(year_to_column.keys())
    if 2030 in all_years:
        all_years.add(2035)
    if 2040 in all_years:
        all_years.add(2045)

    # Step 3: Map Tech_IDs to their corresponding row numbers
    tech_id_to_row = {}
    row = tech_id_row_start
    while True:
        tech_cell = ws.range(f"{tech_id_col}{row}")
        tech_id = tech_cell.value
        if tech_id is None:
            break
        tech_id_to_row[str(tech_id).strip()] = row
        row += 1

    # Step 4: Clear all matching cells for all mapped Tech_IDs
    for tech_ids in tech_to_id.values():
        if not isinstance(tech_ids, list):
            tech_ids = [tech_ids]

        for tech_id in tech_ids:
            row = tech_id_to_row.get(str(tech_id).strip())
            if row is None:
                continue  # Silent skip is OK here
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
