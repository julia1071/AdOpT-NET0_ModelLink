# pip install xlwings
import xlwings as xw
from clear_input_file_IESA import clear_input_file_IESA

def update_input_file_IESA(
    input_path,
    sheet_name,
    tech_id_col,
    tech_id_row_start,
    merged_row,
    header_row,
    merged_name,
    update_data,
    tech_to_id
):
    print("📝 Updating the input file of IESA...")

    # First: Clean old values
    clear_input_file_IESA(
        input_path=input_path,
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
    wb = xw.Book(input_path)
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
    for tech_id, year_vals in update_data.items():
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

    wb.save()
    wb.close()
    app.quit()
    return "✅ All values written successfully."

# updates = {'ICH01_01': {2030: 0.7625683636363622}, 'Amm01_08': {2030: 5.7157959305044255, 2040: 21.231847600630275, 2050: 8.688538732020872}, 'Amm01_05': {2030: 14.707186170425443, 2050: 12.363701694189698}, 'ICH01_14': {2030: 0.6129700727272721, 2040: 0.2929501831695437, 2050: 0.34348699999999927}, 'ICH01_40': {2040: 1.010855734947111, 2050: 1.3738229999999996}, 'ICH01_12': {2040: 0.20549135776519334}}
# tech_to_id = {"CrackerFurnace": "ICH01_01", "CrackerFurnace_CC": "ICH01_02", "CrackerFurnace_CC_bio": "ICH01_03",
#               "CrackerFurnace_Electric": "ICH01_05",
#               "CrackerFurnace_Electric_bio": "ICH01_06", "MTO": "ICH01_12", "PDH": "ICH01_14",
#               "MPW2methanol_input": "WAI01_10", "MPW2methanol_input_CC": "WAI01_11",
#               "MPW2methanol_output": "RFS04_01",
#               "SteamReformer": "Amm01_01", "SteamReformer_CC": "Amm01_02",
#               "AEC": "Amm01_05", "ElectricSMR_m": "Amm01_08", "CO2electrolysis": "ICH01_40"
#               }
#
# input_path = "U:/IESA-Opt-Dev_20250605_linking_correct/data/20250619_detailed_linked.xlsx"
# update_input_file_IESA(input_path,
#                 sheet_name="Technologies",
#                 tech_id_col="A",
#                 tech_id_row_start=7,
#                 merged_row=2,
#                 header_row=5,
#                 merged_name="Minimum use in a year",
#                 update_data=updates,
#                 tech_to_id=tech_to_id)
#
# clear_input_file_IESA(input_path,
#                 sheet_name="Technologies",
#                 tech_id_col="A",
#                 tech_id_row_start=7,
#                 merged_row=2,
#                 header_row=5,
#                 merged_name="Minimum use in a year",
#                 tech_to_id=tech_to_id)
#
