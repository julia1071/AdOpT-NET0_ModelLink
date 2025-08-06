import numpy as np
import xlwings as xw

import config_model_linking as cfg


def update_input_file_IESA(sheet_name, tech_id_col, tech_id_row_start, merged_row, header_row, merged_name,
                           update_data, tech_to_id):
    print("📝 Updating the input file of IESA...")

    # First: Clean old values
    clear_input_file_IESA(
        sheet_name=sheet_name,
        tech_id_col=tech_id_col,
        tech_id_row_start=tech_id_row_start,
        merged_row=merged_row,
        header_row=header_row,
        merged_name=merged_name,
        tech_to_id=tech_to_id
    )

    # Then: Re-open to write values
    app = xw.App(visible=False)
    wb = xw.Book(cfg.IESA_input_data_path)
    ws = wb.sheets[sheet_name]

    # Find merged header
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

    # Map years to columns
    year_to_column = {}
    for col in range(merged_range.column, merged_range.last_cell.column + 1):
        val = ws.range((header_row, col)).value
        try:
            year = int(float(str(val).strip()))
            year_to_column[year] = col
        except (ValueError, TypeError):
            continue

    # Map Tech_IDs to rows
    tech_id_to_row = {}
    row = tech_id_row_start
    while True:
        tech_cell = ws.range(f"{tech_id_col}{row}")
        tech_id = tech_cell.value
        if tech_id is None:
            break
        tech_id_to_row[str(tech_id).strip()] = row
        row += 1

    # Expand data
    expanded_update_data = {}
    for tech_id, year_vals in update_data["AnnualOutput"].items():
        expanded_year_vals = {}
        sorted_years = sorted(year_vals.keys())
        for year in sorted_years:
            expanded_year_vals[year] = year_vals[year]
            if year == 2030 and 2035 not in year_vals:
                expanded_year_vals[2035] = year_vals[year]
            if year == 2040 and 2045 not in year_vals:
                expanded_year_vals[2045] = year_vals[year]
        expanded_update_data[tech_id] = expanded_year_vals

    # Write new values
    for tech_id, year_vals in expanded_update_data.items():
        if tech_id not in tech_id_to_row:
            raise ValueError(
                f"❌ Tech_ID '{tech_id}' from the update_data is not found in the sheet '{sheet_name}'.\n"
                f"Check if the input file includes this technology under column '{tech_id_col}' starting from row {tech_id_row_start}."
            )

        for year, val in year_vals.items():
            col = year_to_column.get(year)
            if col is None:
                raise ValueError(
                    f"❌ Year '{year}' for Tech_ID '{tech_id}' is not found in the Excel sheet under merged header '{merged_name}'.\n"
                    f"Check if the year {year} exists in the header row {header_row} within the merged block."
                )

            row = tech_id_to_row[tech_id]
            print(f"✍️ Writing {val} to row {row}, col {col} (Tech_ID={tech_id}, Year={year})")
            ws.range((row, col)).value = val

    if cfg.linking_operation:
        update_operations_IESA(sheet_name="HourlyProfiles",
                               header_row=3,
                               profile_row_start=5,
                               update_data=update_data)

    wb.save()
    wb.close()
    app.quit()
    return "✅ All values written successfully."


def clear_input_file_IESA(sheet_name, tech_id_col, tech_id_row_start, merged_row, header_row, merged_name, tech_to_id):
    """
    Clears all input values in the specified Excel sheet related to the given Tech_IDs and years,
    based on a merged header. Supports both one-to-one and one-to-many tech_to_id mappings.

    Args:
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
    wb = xw.Book(cfg.IESA_input_data_path)
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

    clear_input_operations_IESA(sheet_name="HourlyProfiles",
                                header_row=3,
                                profile_row_start=5)

    wb.save()
    wb.close()
    app.quit()
    print("✅ IESA input file cleaned successfully.")


def update_operations_IESA(sheet_name, header_row, profile_row_start, update_data):
    """
    Updates IESA Excel sheet with average operation profiles per technology,
    averaged over available years (ignoring None entries).

    Args:
        sheet_name (str): Sheet name in the Excel file.
        header_row (int): Row number containing technology names as headers.
        profile_row_start (int): First row where the 8760 profile begins.
        update_data (dict): {"Operation": {tech: {year: array or None}}}
    """
    print("📄 Updating IESA operation profiles with averaged data...")

    # Start Excel and open workbook
    app = xw.App(visible=False)
    wb = xw.Book(cfg.IESA_input_data_path)
    ws = wb.sheets[sheet_name]

    # Get header row values (tech names from columns 22–26)
    headers = ws.range((header_row, 22), (header_row, 26)).value
    start_col = 22  # Excel column V

    # Build average profiles: {tech: avg_array}
    avg_profiles = {}
    for tech, year_data in update_data.get("Operation", {}).items():
        valid_profiles = [np.array(profile) for profile in year_data.values() if profile is not None]
        if valid_profiles:
            avg_profiles[tech] = np.mean(valid_profiles, axis=0)

    # Write to sheet using correct column indices
    for col_offset, header in enumerate(headers):
        col_idx = start_col + col_offset
        if header in avg_profiles:
            profile = avg_profiles[header]
            if not np.isnan(profile).all():
                profile = np.array(profile, dtype=float)  # force numeric type
                write_range = ws.range(
                    (profile_row_start, col_idx),
                    (profile_row_start + len(profile) - 1, col_idx)
                )
                write_range.value = [[float(val)] for val in profile]
                # write_range.number_format = "0.000000"
                print(f"✅ Wrote averaged profile for {header} in column {col_idx}")

    print("💾 Averaged IESA operation profiles written successfully.")


def clear_input_operations_IESA(sheet_name, header_row, profile_row_start):
    """
    Clears the IESA Excel sheet with a default operation profile of 1/8760
    for each hour of the year for each technology.

    Args:
        sheet_name (str): Sheet name in the Excel file.
        header_row (int): Row number containing technology names as headers.
        profile_row_start (int): First row where the 8760 profile begins.
    """
    print("🧹 Clearing IESA operation profiles to default...")

    # Start Excel and open workbook
    app = xw.App(visible=False)
    wb = xw.Book(cfg.IESA_input_data_path)
    ws = wb.sheets[sheet_name]

    # Read headers from columns 22–26 (Excel columns V to Z)
    headers = ws.range((header_row, 22), (header_row, 26)).value
    start_col = 22  # Starting at Excel column V

    # Default profile: 1/8760 for each hour
    profile = np.full(8760, 1.0 / 8760, dtype=float)

    for col_offset, header in enumerate(headers):
        col_idx = start_col + col_offset

        write_range = ws.range(
            (profile_row_start, col_idx),
            (profile_row_start + len(profile) - 1, col_idx)
        )
        write_range.value = [[float(val)] for val in profile]
        # write_range.number_format = "0.00000000"
