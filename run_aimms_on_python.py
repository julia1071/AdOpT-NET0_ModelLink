import subprocess
import os

def run_IESA_change_name_files(i, command, original_name_output, original_name_input, new_name_output, new_name_input, map_name_IESA):
    print(f"Iteration: {i}")
    print("Running AIMMS")

    subprocess.call(command)
    print("AIMMS exited")

    # New filenames
    output_filename = f"ResultsModelLinking_General_Iteration_{i}.xlsx"
    input_filename = f"Input_Iteration_{i}.xlsx"
    nno = map_name_IESA / output_filename
    nni = map_name_IESA / input_filename

    try:
        os.rename(original_name_output, nno)
        print(f"✔ Output file moved to: {nno}")
    except FileNotFoundError:
        print(f"❌ Output file not found: {original_name_output}")
        return
    except FileExistsError:
        print(f"❌ File already exists: {nno}")
    except Exception as e:
        print(f"❌ Error while renaming output: {e}")

    try:
        os.rename(original_name_input, nni)
        print(f"✔ Input file moved to: {nni}")
    except FileNotFoundError:
        print(f"❌ Input file not found: {original_name_input}")
        return
    except FileExistsError:
        print(f"❌ File already exists: {nni}")
    except Exception as e:
        print(f"❌ Error while renaming input: {e}")

    return nno  # optionally return (nno, nni) if both paths are needed
