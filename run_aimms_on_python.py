import subprocess
import os


run_from_server = 1

if run_from_server:
    aimms_path = "C:\\Program Files (x86)\\AIMMS\\IFA\\Aimms\\25.3.4.2-x64-VS2022\\Bin\\aimms.exe"
else:
    aimms_path = "C:\\Program Files\\Aimms-25.3.4.2-x64-VS2022.exe" #Path on your local computer


# Define the file path to the model and the procedures that you want to run,.
command = [
        aimms_path,
        "U:\\IESA-Opt-ModelLinking\\ModelLinking.aimms", "--end-user",
        "--run-only", "Run_IESA"
    ]

# Pick the file path where AIMMS is saving the results of the optimization.
# The name of the initial results document can be adjusted in AIMMS "Settings_Solve_Transition".
original_name_output = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General.xlsx"

#The input file name can be changed in AIMMS right clicking on the procedure "runDataReading" selecting attributes
#!Make sure that the output folder is empty and does not contain results from a previous run!
original_name_input = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/20250430_detailed.xlsx"

#Define the new name of the input and output file
new_name_output = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General_Iteration_"
new_name_input = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/Input_Iteration_"

def run_IESA_change_name_files(i,command, original_name_output, original_name_input, new_name_output, new_name_input):
    print("Iteration:", i)
    print("Running AIMMS")
    # Run the command
    ret = subprocess.call(command)
    print("AIMMS exited")
    #Define the new name of the new document inserting the iteration number
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