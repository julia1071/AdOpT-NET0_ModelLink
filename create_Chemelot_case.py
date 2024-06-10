from pathlib import Path
import src.data_preprocessing as dp
import pandas as pd
from src.energyhub import EnergyHub
from src.result_management.read_results import add_values_to_summary

#Create data Chemelot cluster
execute = 1

if execute == 1:
    # Specify the path to your input data
    casepath = "Z:/PyHub/PyHub_casestudies/CM/Chemelot_cluster"
    datapath = "Z:/PyHub/PyHub_data/CM/100624_CM"
    resultpath = "Z:/PyHub/PyHub_results/CM/Chemelot_fullres"

    #Set up case study for the first time

    firsttime = 0
    if firsttime == 1:
        # Create template files
        dp.create_optimization_templates(casepath)
        dp.create_montecarlo_template_csv(casepath)

        # Create folder structure
        dp.create_input_data_folder_template(casepath)

        # # Copy technology and network data into folder
        dp.copy_technology_data(casepath, datapath)

        # Read climate data and fill carried data
        dp.load_climate_data_from_api(casepath)
        dp.fill_carrier_data(casepath, value_or_data=0)

        # Demand data
        dp.fill_carrier_data(casepath, value_or_data=135, columns=['Demand'], carriers=['ammonia'])
        dp.fill_carrier_data(casepath, value_or_data=45, columns=['Demand'], carriers=['CO2pure'])
        dp.fill_carrier_data(casepath, value_or_data=150, columns=['Demand'], carriers=['ethylene'])

        # No import limit
        dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Import limit'], carriers=['electricity', 'methane', 'naphtha'])

        # No export limit
        dp.fill_carrier_data(casepath, value_or_data=2000, columns=['Import limit'], carriers=['nitrogen', 'oxygen', 'heatlowT', 'steam', 'crackergas'])

        # Constant prices
        dp.fill_carrier_data(casepath, value_or_data=35, columns=['Import price'], carriers=['methane'])
        dp.fill_carrier_data(casepath, value_or_data=732, columns=['Import price'], carriers=['naphtha'])

    # Electricity price from file
    el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_CM.csv'
    el_importdata = pd.read_csv(el_load_path, sep=';', header=0, nrows=8760)
    el_price = el_importdata.iloc[:, 0]
    el_emissionrate = el_importdata.iloc[:, 3]

    dp.fill_carrier_data(casepath, value_or_data=el_price, columns=['Import price'], carriers=['electricity'])
    dp.fill_carrier_data(casepath, value_or_data=el_emissionrate, columns=['Import emission factor'], carriers=['electricity'])
