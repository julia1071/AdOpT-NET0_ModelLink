import pandas as pd
import os


def conversion_factor_cluster_to_IESA(tech_id):
    """
    Returns a conversion factor to translate from cluster units to IESA-Opt units,
    based on the given technology ID.
    Fails explicitly if the tech_id is unknown.
    """

    if tech_id in ['ICH01_01', 'ICH01_02', 'ICH01_03', 'ICH01_05', 'ICH01_06']:
        # Cluster: t olefins/y → IESA: Mton Ey/y
        return 0.303 / 10**6

    elif tech_id in ['ICH01_11','ICH01_40']:
        # Cluster: t ethylene/y → IESA: Mton Ey/y
        return 1 / 10**6

    elif tech_id in ['ICH01_12', 'ICH01_14']:
        # Cluster: t propylene/y → IESA: Mton Py/y
        return 1 / 10**6

    elif tech_id in ['WAI01_10', 'WAI01_11'] :
        # Cluster: t MPW/y → IESA: PJ/y (Syngas)
        return 1

    elif tech_id in ['RFS04_01', 'RFS04_02']:
        # Cluster: t methanol/y → IESA: PJ/y (Methanol)
        return 19.9 / 10**6

    elif tech_id in ['Amm01_01', 'Amm01_02', 'Amm01_05']:
        # Cluster: MWh → IESA: PJ/y (Ammonia)
        return (0.168 * 18.72) / 10**6

    elif tech_id == 'Amm01_08':
        # Cluster: MWh feedgas → IESA: PJ/y (Ammonia)
        return (4.966 * 0.168 * 18.72) / 10**6

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

    if "Periods" not in df.columns or "World Development Indicators" not in df.columns:
        raise ValueError(f"❌ Missing required columns: 'Periods' and/or 'World Development Indicators' in sheet '{sheet_name}'")

    # --- Prepare data ---
    df["Periods"] = df["Periods"].astype(int)
    df.set_index("Periods", inplace=True)

    # --- Check if both years exist ---
    missing_years = []
    for year in [baseyear_cluster, baseyear_IESA]:
        if year not in df.index:
            missing_years.append(year)

    if missing_years:
        raise ValueError(f"❌ Missing indicator data for year(s): {missing_years} in sheet '{sheet_name}'")

    # --- Calculate conversion factor ---
    ppi_cluster = df.loc[baseyear_cluster, "World Development Indicators"]
    ppi_iesa = df.loc[baseyear_IESA, "World Development Indicators"]

    factor = ppi_cluster / ppi_iesa
    return factor

def conversion_factor_IESA_to_cluster(sheet, filter, ppi_file_path, baseyear_cluster, baseyear_IESA):
    if sheet == 'EnergyCosts':
        if filter in ['Naphtha', 'Bio Naphtha']:
            sheet_name = 'World Development Indicators'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 44.9  # Meuro/PJ to euro/t
        elif filter in ['Natural Gas HD']:
            sheet_name = 'World Development Indicators'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 3.6 # Meuro/PJ to euro/MWh
        elif filter in ['methane_bio']:
            sheet_name = 'World Development Indicators'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 3.6 # Meuro/PJ to euro/MWh
        elif filter == 'Biomass':
            sheet_name = 'World Development Indicators'
            ppi_cf = get_ppi_conversion_factor(ppi_file_path, sheet_name, baseyear_cluster, baseyear_IESA)
            return ppi_cf * 14.7 # Meuro/PJ to euro/t
        else:
            raise ValueError(f"❌ Undefined filter '{filter}' for sheet '{sheet}'.")

    elif sheet == 'SupplyDemand':
        if filter in ['WAI01_01', 'WAI01_02', 'EPO01_03']:
            return (1 / 8760) * 10**6  # Mton/year to t/hour
        else:
            raise ValueError(f"❌ Undefined filter '{filter}' for sheet '{sheet}'.")

    else:
        raise ValueError(f"❌ Undefined sheet '{sheet}' in conversion logic.")
