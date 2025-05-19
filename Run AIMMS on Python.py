import subprocess
import os

iterations = 3 #Now I adjust this manually but it could be coded such that the loop stops on a certain condition when comparing data.

# Define the AIMMS executable and the model path and the procedure in AIMMS that you want to run
command = [
        "U:\\Aimms-25.4.1.2-x64-VS2022.exe",
        "U:\\IESA-Opt-ModelLinking\\ModelLinking.aimms",
        "--run-only", "Run_IESA"
    ]

#Pick the file path where AIMMS is saving the results of the optimization. The name of the initial results document can be adjusted in AIMMS "Settings_Solve_Transition".
#WARNING! IF the path is changed, this should also be changed inside the function!
original_name = "U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General.xlsx"

def new_name_results_iesa(iterations,command,original_name):
    for i in range (iterations): #This should be the main loop. One iteration of IESA is used for 2030,2040,2050. Cluster model is running for the three separate years.
        print("Iteration:",i+1)

        # Run the command
        ret = subprocess.call(command)

        #Define the new name of the new document inserting the iteration number
        new_name = f"U:/IESA-Opt-ModelLinking/Output/ResultsModelLinking/ResultsModelLinking_General_Iteration_{i + 1}.xlsx"

        try:
            os.rename(original_name, new_name)
            print(f"✔ File renamed to: {new_name}")
        except FileNotFoundError:
            print("❌ Original file not found. It may have already been moved.")
            break  # Stop if the original file no longer exists
        except FileExistsError:
            print(f"❌ File already exists: {new_name}")
        except Exception as e:
            print(f"❌ An error occurred: {e}")

        print("AIMMS exited with code:", ret)