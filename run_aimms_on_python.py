import subprocess
import os

def run_IESA_change_name_files(i,command, original_name_output, original_name_input, new_name_output, new_name_input):
    print("Iteration:", i)
    print("Running AIMMS")

    # Run the command
    subprocess.call(command)

    print("AIMMS exited")

    # Define the new name of the new document inserting the iteration number
    nno = f"{new_name_output}{i}.xlsx"
    nni = f"{new_name_input}{i}.xlsx"

    try:
        os.rename(original_name_output, nno)
        print(f"✔ File renamed to: {nno}")
    except FileNotFoundError:
        print(f"❌ Original file not found. Check if the output name in AIMMS corresponds to: {original_name_output}")
        return
    except FileExistsError:
        print(f"❌ File already exists: {nno}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


    try:
        os.rename(original_name_input, nni)
        print(f"✔ File renamed to: {nni}")
    except FileNotFoundError:
        print(f"❌ Original file not found. Check if the output name in AIMMS corresponds to: {original_name_input}")
        return
    except FileExistsError:
        print(f"❌ File already exists: {nni}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


    return nno