from pathlib import Path
import src.data_preprocessing as dp
from src.energyhub import EnergyHub
from src.result_management.read_results import add_values_to_summary

#Run Chemelot case study
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    datapath = "Z:/PyHub/PyHub_data/CM/100624_CM"
    resultpath = "Z:/PyHub/PyHub_results/CM/Chemelot_fullres"

    # Construct and solve the model
    pyhub = EnergyHub()
    pyhub.read_data(casepath)
    pyhub.quick_solve()

    # # Add values of (part of) the parameters and variables to the summary file
    # add_values_to_summary(Path(resultpath))
