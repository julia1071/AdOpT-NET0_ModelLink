import subprocess
import os
from pathlib import Path


def run_IESA_change_name_files(i, command, original_name_output, original_name_input,
                                output_basename, input_basename, map_name_IESA):
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
    print(f"Iteration: {i}")
    print("Running AIMMS")

    subprocess.call(command)
    print("AIMMS exited")

    output_filename = f"{output_basename}{i}.xlsx"
    input_filename = f"{input_basename}{i}.xlsx"
    nno = map_name_IESA / output_filename
    nni = map_name_IESA / input_filename

    # Rename output
    try:
        os.rename(original_name_output, nno)
        print(f"✔ Output file moved to: {nno}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Original output file not found: {original_name_output}")
    except FileExistsError:
        raise FileExistsError(f"New output file already exists: {nno}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while renaming output: {e}")

    # Rename input
    try:
        os.rename(original_name_input, nni)
        print(f"✔ Input file moved to: {nni}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Original input file not found: {original_name_input}")
    except FileExistsError:
        raise FileExistsError(f"New input file already exists: {nni}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while renaming input: {e}")

    return nno


