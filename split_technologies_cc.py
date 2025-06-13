from pathlib import Path
import pandas as pd
import h5py
from adopt_net0 import extract_datasets_from_h5group
from conversion_factors import conversion_factor_cluster_to_IESA


# --- Configuration ---
result_folder = Path("U:/Data AdOpt-NET0/Model_Linking/Results/Zeeland")
intervals = ["2030", "2040", "2050"]
location = "Zeeland"

tech_size_dict = {
    ('Zeeland', '2030', 'AEC'): 0.0,
    ('Zeeland', '2040', 'AEC'): 0.0,
    ('Zeeland', '2050', 'AEC'): 0.0,
    ('Zeeland', '2030', 'ASU'): 0.0,
    ('Zeeland', '2040', 'ASU'): 2.795716447419882,
    ('Zeeland', '2050', 'ASU'): 0.0,
    ('Zeeland', '2030', 'Boiler_El'): 0.0,
    ('Zeeland', '2040', 'Boiler_El'): 0.0,
    ('Zeeland', '2050', 'Boiler_El'): 0.0,
    ('Zeeland', '2030', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2040', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2050', 'Boiler_Industrial_NG'): 0.0,
    ('Zeeland', '2030', 'CO2_mixer'): 0.0,
    ('Zeeland', '2040', 'CO2_mixer'): 209.01909638977068,
    ('Zeeland', '2050', 'CO2_mixer'): 0.0,
    ('Zeeland', '2030', 'CO2toEmission'): 0.0,
    ('Zeeland', '2040', 'CO2toEmission'): 0.0,
    ('Zeeland', '2050', 'CO2toEmission'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_Electric'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2040', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2050', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2030', 'EDH'): 0.0,
    ('Zeeland', '2040', 'EDH'): 0.0,
    ('Zeeland', '2050', 'EDH'): 0.0,
    ('Zeeland', '2030', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2040', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2050', 'ElectricSMR_m'): 0.0,
    ('Zeeland', '2030', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2040', 'HBfeed_mixer'): 80.45227231021265,
    ('Zeeland', '2050', 'HBfeed_mixer'): 0.0,
    ('Zeeland', '2030', 'HaberBosch'): 0.0,
    ('Zeeland', '2040', 'HaberBosch'): 5.508454311444429e-08,
    ('Zeeland', '2050', 'HaberBosch'): 0.0,
    ('Zeeland', '2030', 'HaberBosch_existing'): 0.0,
    ('Zeeland', '2040', 'HaberBosch_existing'): 80.45227223309429,
    ('Zeeland', '2050', 'HaberBosch_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol'): 0.0,
    ('Zeeland', '2050', 'MPW2methanol'): 0.0,
    ('Zeeland', '2030', 'MTO'): 0.0,
    ('Zeeland', '2040', 'MTO'): 0.0,
    ('Zeeland', '2050', 'MTO'): 0.0,
    ('Zeeland', '2030', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2040', 'MeOHsynthesis'): 133.78620424057752,
    ('Zeeland', '2050', 'MeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2040', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2050', 'OlefinSeparation'): 0.0,
    ('Zeeland', '2030', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2040', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2050', 'OlefinSeparation_existing'): 0.0,
    ('Zeeland', '2030', 'PDH'): 0.0,
    ('Zeeland', '2040', 'PDH'): 36.97144365819727,
    ('Zeeland', '2050', 'PDH'): 0.0,
    ('Zeeland', '2030', 'RWGS'): 0.0,
    ('Zeeland', '2040', 'RWGS'): 0.0,
    ('Zeeland', '2050', 'RWGS'): 0.0,
    ('Zeeland', '2030', 'SteamReformer'): 105.71914879513074,
    ('Zeeland', '2040', 'SteamReformer'): 0.0,
    ('Zeeland', '2050', 'SteamReformer'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2040', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2050', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_Battery'): 0.0,
    ('Zeeland', '2040', 'Storage_Battery'): 4065.0,
    ('Zeeland', '2050', 'Storage_Battery'): 0.0,
    ('Zeeland', '2030', 'Storage_CO2'): 0.0,
    ('Zeeland', '2040', 'Storage_CO2'): 0.0,
    ('Zeeland', '2050', 'Storage_CO2'): 0.0,
    ('Zeeland', '2030', 'Storage_H2'): 0.0,
    ('Zeeland', '2040', 'Storage_H2'): 6.109531913381054e-08,
    ('Zeeland', '2050', 'Storage_H2'): 0.0,
    ('Zeeland', '2030', 'WGS_m'): 0.0,
    ('Zeeland', '2040', 'WGS_m'): 13.889717300760989,
    ('Zeeland', '2050', 'WGS_m'): 0.0,
    ('Zeeland', '2030', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2040', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2050', 'feedgas_mixer'): 0.0,
    ('Zeeland', '2030', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2040', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2050', 'naphtha_mixer'): 0.0,
    ('Zeeland', '2030', 'syngas_mixer'): 0.0,
    ('Zeeland', '2040', 'syngas_mixer'): 0.0,
    ('Zeeland', '2050', 'syngas_mixer'): 0.0,
    ('Zeeland', '2030', 'Boiler_El_existing'): 0.0,
    ('Zeeland', '2040', 'Boiler_El_existing'): 532.0052720677872,
    ('Zeeland', '2050', 'Boiler_El_existing'): 0.0,
    ('Zeeland', '2030', 'Boiler_Industrial_NG_existing'): 0.0,
    ('Zeeland', '2040', 'Boiler_Industrial_NG_existing'): 386.7784939674664,
    ('Zeeland', '2050', 'Boiler_Industrial_NG_existing'): 0.0,
    ('Zeeland', '2030', 'CO2_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'CO2_mixer_existing'): 80.58255938324403,
    ('Zeeland', '2050', 'CO2_mixer_existing'): 0.0,
    ('Zeeland', '2030', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2040', 'CO2electrolysis'): 206.9747557802476,
    ('Zeeland', '2050', 'CO2electrolysis'): 0.0,
    ('Zeeland', '2030', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2040', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2050', 'DirectMeOHsynthesis'): 0.0,
    ('Zeeland', '2030', 'EDH_existing'): 0.0,
    ('Zeeland', '2040', 'EDH_existing'): 136.46232791347748,
    ('Zeeland', '2050', 'EDH_existing'): 0.0,
    ('Zeeland', '2030', 'ElectricSMR_m_existing'): 0.0,
    ('Zeeland', '2040', 'ElectricSMR_m_existing'): 1917.3486711614985,
    ('Zeeland', '2050', 'ElectricSMR_m_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol_existing'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_existing'): 66.37225877872193,
    ('Zeeland', '2050', 'MPW2methanol_existing'): 0.0,
    ('Zeeland', '2030', 'MTO_existing'): 0.0,
    ('Zeeland', '2040', 'MTO_existing'): 392.649098245147,
    ('Zeeland', '2050', 'MTO_existing'): 0.0,
    ('Zeeland', '2030', 'MeOHsynthesis_existing'): 0.0,
    ('Zeeland', '2040', 'MeOHsynthesis_existing'): 358.54420150720046,
    ('Zeeland', '2050', 'MeOHsynthesis_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_Battery_existing'): 0.0,
    ('Zeeland', '2040', 'Storage_Battery_existing'): 1448.4999281179907,
    ('Zeeland', '2050', 'Storage_Battery_existing'): 0.0,
    ('Zeeland', '2030', 'Storage_CO2_existing'): 0.0,
    ('Zeeland', '2040', 'Storage_CO2_existing'): 4481.695179214337,
    ('Zeeland', '2050', 'Storage_CO2_existing'): 0.0,
    ('Zeeland', '2030', 'feedgas_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'feedgas_mixer_existing'): 2026.3765796917955,
    ('Zeeland', '2050', 'feedgas_mixer_existing'): 0.0,
    ('Zeeland', '2030', 'syngas_mixer_existing'): 0.0,
    ('Zeeland', '2040', 'syngas_mixer_existing'): 358.5442015072002,
    ('Zeeland', '2050', 'syngas_mixer_existing'): 0.0,
}
cc_fraction_dict = {
    ('Zeeland', '2030', 'CrackerFurnace'): 0.0,
    ('Zeeland', '2030', 'CrackerFurnace_existing'): 0.0,
    ('Zeeland', '2030', 'MPW2methanol'): 0.8653873120759433,
    ('Zeeland', '2030', 'SteamReformer'): 0.0,
    ('Zeeland', '2030', 'SteamReformer_existing'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol'): 0.0,
    ('Zeeland', '2040', 'MPW2methanol_existing'): 0.8882601856773454,
    ('Zeeland', '2040', 'SteamReformer_existing'): 0.0,
}
def apply_cc_splitting(tech_size_dict, cc_fraction_dict, capture_rate=0.9):
    """
    For each technology in cc_fraction_dict:
    - Splits the value in tech_size_dict into a CC and non-CC part.
    - Adds a new entry with name `technology_CC` or `technology_CC_existing`
    - Updates the original entry to its non-CC share.

    Returns a new updated dictionary.
    """
    updated_dict = tech_size_dict.copy()

    for (location, interval, tech), cc_frac in cc_fraction_dict.items():
        if (location, interval, tech) not in tech_size_dict:
            print(f"No original size of {tech} in {tech_size_dict}")

        original_size = tech_size_dict[(location, interval, tech)]

        # Calculate shares
        cc_ratio = cc_frac / capture_rate
        non_cc_ratio = 1 - cc_ratio

        size_cc = original_size * cc_ratio
        size_non_cc = original_size * non_cc_ratio

        # Build new tech name (preserve "_existing" if present)
        if tech.endswith("_existing"):
            base_tech = tech.replace("_existing", "")
            new_tech = f"{base_tech}_CC_existing"
        else:
            new_tech = f"{tech}_CC"

        # Add to updated dictionary
        updated_dict[(location, interval, new_tech)] = size_cc
        updated_dict[(location, interval, tech)] = size_non_cc  # overwrite

    return updated_dict


print(apply_cc_splitting(tech_size_dict, cc_fraction_dict, capture_rate=0.9))