import pandas as pd
import os

def conversion_factor_cluster_to_IESA(tech_id):
    """
    Returns a conversion factor to translate from cluster units to IESA-Opt units,
    based on the given technology ID.
    Fails explicitly if the tech_id is unknown.
    """

    if tech_id in ['ICH01_01', 'ICH01_05']:
        # Cluster: t naphtha/h → IESA: Mton Ey/y
        return (0.303 * 8760) / 10**6

    elif tech_id == 'ICH01_11':
        # t ethanol/h → Mton Ey/y
        return (0.592 * 8760) / 10**6

    elif tech_id == 'ICH01_12':
        # t methanol/h → Mton Ey/y
        return (0.163 * 8760) / 10**6

    elif tech_id == 'ICH01_14':
        # t propane/h → Mton Py/y
        return (0.859 * 8760) / 10**6

    elif tech_id == 'RFS04_01':
        # t plastic/h → Methanol PJ/y
        return (8760 / 10**6) * (1 / 0.034184528)

    elif tech_id == 'HTI01_16':
        # t CO₂/h → Syngas PJ/y
        return (8760 / 10**6) * (1 / 0.077974811)

    elif tech_id == 'RFS04_02':
        # t CO₂/h → Methanol PJ/y
        return (0.67907103 * 8760 * 19.9) / 10**6

    elif tech_id == 'Amm01_01':
        # MWh natural gas → Ammonia PJ/y
        return (0.761 * 0.168) * (18.72 / 10**6)

    elif tech_id == 'Amm01_05':
        # MWh electricity → Ammonia PJ/y
        return (0.629 * 0.168) * (18.72 / 10**6)

    elif tech_id == 'Amm01_08':
        # MWh feedgas → Ammonia PJ/y
        return (0.927 * 0.168) * (18.72 / 10**6)

    elif tech_id == 'ICH01_40':
        # t CO₂/h → Mton Ey/y
        return (8760 * 0.602) / 10**6

    else:
        raise ValueError(f"❌ Conversion factor for tech_id '{tech_id}' is not defined.")


def get_ppi_conversion_factor(PPI_file_path, sheet_name, baseyear_cluster, baseyear_IESA):
    """
    Converts values from IESA base year to cluster base year using CBS PPI data.
    Handles errors for missing file, sheet, or years.

    Returns:
        float: conversion factor = PPI_cluster / PPI_IESA
    """
    # --- Check if file exists ---
    if not os.path.exists(PPI_file_path):
        raise FileNotFoundError(f"❌ File not found: {PPI_file_path}")

    try:
        xls = pd.ExcelFile(PPI_file_path)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to open Excel file: {e}")

    # --- Check if sheet exists ---
    if sheet_name not in xls.sheet_names:
        raise ValueError(f"❌ Sheet '{sheet_name}' not found. Available sheets: {xls.sheet_names}")

    # --- Read sheet and check columns ---
    df = pd.read_excel(xls, sheet_name=sheet_name)

    if "Periods" not in df.columns or "PPI" not in df.columns:
        raise ValueError(f"❌ Missing required columns: 'Periods' and/or 'PPI' in sheet '{sheet_name}'")

    # --- Prepare data ---
    df["Periods"] = df["Periods"].astype(int)
    df.set_index("Periods", inplace=True)

    # --- Check if both years exist ---
    missing_years = []
    for year in [baseyear_cluster, baseyear_IESA]:
        if year not in df.index:
            missing_years.append(year)

    if missing_years:
        raise ValueError(f"❌ Missing PPI data for year(s): {missing_years} in sheet '{sheet_name}'")

    # --- Calculate conversion factor ---
    ppi_cluster = df.loc[baseyear_cluster, "PPI"]
    ppi_iesa = df.loc[baseyear_IESA, "PPI"]

    factor = ppi_cluster / ppi_iesa
    return factor

def conversion_factor_IESA_to_cluster(sheet, filter, ppi_file_path, baseyear_cluster, baseyear_IESA):
    if sheet == 'EnergyCosts':
        if filter in ['Naphtha', 'Bio Naphtha']:
            sheet_name = 'Crude petroleum and natural gas'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 44.9  # Meuro/PJ to euro/t
        elif filter in ['Methane', 'Bio Methane']:
            sheet_name = 'Crude petroleum and natural gas'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 50.04
        elif filter == 'Biomass':
            sheet_name = 'Wood(products)'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 50.04
        else:
            raise ValueError(f"❌ Undefined filter '{filter}' for sheet '{sheet}'.")

    elif sheet == 'Configuration_Stock':
        if filter == 'WAI01_02':
            return (1 / 8760) * 10**6  # Mton/year to ton/hour
        else:
            raise ValueError(f"❌ Undefined filter '{filter}' for sheet '{sheet}'.")

    else:
        raise ValueError(f"❌ Undefined sheet '{sheet}' in conversion logic.")
