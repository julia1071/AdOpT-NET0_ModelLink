import subprocess
import os
from pathlib import Path

import config_model_linking as cfg


def run_IESA_change_name_files(iteration, map_name_IESA):
    """
    Runs the AIMMS IESA-Opt model, then renames and moves the input and output Excel files
    for the current iteration.

    Raises:
        FileNotFoundError: If the AIMMS output or input file is missing
        FileExistsError: If the target output or input file already exists
        RuntimeError: For other unexpected renaming issues

    Returns:
        Path: The path to the newly renamed output file
    """
    print(f"Iteration: {iteration}")
    print("Running AIMMS")

    subprocess.call(cfg.command)
    print("AIMMS exited")

    output_filename = f"{cfg.basename_new_output_IESA}{iteration}.xlsx"
    input_filename = f"{cfg.basename_new_input_IESA}{iteration}.xlsx"
    new_name_output = map_name_IESA / output_filename
    new_name_input = map_name_IESA / input_filename

    # Rename output
    try:
        os.rename(cfg.original_filename_output_IESA, new_name_output)
        print(f"✔ Output file moved to: {new_name_output}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Original output file not found: {cfg.original_filename_output_IESA}")
    except FileExistsError:
        raise FileExistsError(f"New output file already exists: {new_name_output}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while renaming output: {e}")

    # Rename input
    try:
        os.rename(cfg.original_filename_input_IESA, new_name_input)
        print(f"✔ Input file moved to: {new_name_input}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Original input file not found: {cfg.original_filename_input_IESA}")
    except FileExistsError:
        raise FileExistsError(f"New input file already exists: {new_name_input}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while renaming input: {e}")

    return new_name_output


