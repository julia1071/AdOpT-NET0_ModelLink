import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from cmcrameri import cm


execute = 0

if execute == 1:
    # === PATHS & SETTINGS ===
    datapath = "Z:/AdOpt_NET0/AdOpt_data/Model_Linking/250619_ML_Data_Zeeland_bf"
    savepath = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/"
    el_load_path = Path(datapath) / 'import_data' / 'Electricity_data_ML.xlsx'
    save = 1

    # === YEARS & COLORS ===
    nodes = ['Zeeland']
    years = ['2030', '2040', '2050']
    labels = {'2030': '2030', '2040': '2040', '2050': '2050'}

    colors_zeeland = cm.devon(np.linspace(0, 0.8, len(years)))
    colors_emission = cm.grayC(np.linspace(0, 0.8, len(years)))

    # === LOAD DATA ===
    data = {node: {} for node in nodes}
    for year in years:
        el_importdata = pd.read_excel(el_load_path, sheet_name=year, header=0, nrows=8760)
        for node in nodes:
            if node == 'Chemelot':
                data[node][year] = {
                    'price': el_importdata.iloc[:, 0],
                    'emission': el_importdata.iloc[:, 2] * 1000
                }
            elif node == 'Zeeland':
                data[node][year] = {
                    'price': el_importdata.iloc[:, 1],
                    'emission': el_importdata.iloc[:, 2] * 1000
                }

    # === MATPLOTLIB CONFIG ===
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "axes.labelsize": 10,
        "font.size": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })

    # === FIGURE 1: HOURLY PROFILES ===
    fig1, axes1 = plt.subplots(2, 1, figsize=(6, 5), sharex=True)
    fig1.subplots_adjust(hspace=0.4, top=0.95, bottom=0.1, left=0.1, right=0.98)

    # Top panel: Zeeland Price
    ax_price = axes1[0]
    for i, year in enumerate(years):
        ax_price.plot(
            data['Zeeland'][year]['price'],
            color=colors_zeeland[i],
            label=f"{labels[year]} ({data['Zeeland'][year]['price'].mean():.1f} EUR/MWh)",
            linewidth=0.5
        )
    ax_price.set_title('Electricity Prices: Zeeland')
    ax_price.set_ylabel('Electricity Price [EUR/MWh]')
    ax_price.set_xlim(0, 8759)
    ax_price.set_ylim(0, 550)
    ax_price.legend(loc='upper right')

    # Bottom panel: Emission Rate
    ax_emiss = axes1[1]
    for i, year in enumerate(years):
        ax_emiss.plot(
            data['Zeeland'][year]['emission'],
            color=colors_emission[i],
            label=f"{labels[year]} ({data['Zeeland'][year]['emission'].mean():.0f} kg CO$_2$/MWh)",
            linewidth=0.5
        )
    ax_emiss.set_title('Emission Rates')
    ax_emiss.set_xlabel('Time (hours)')
    ax_emiss.set_ylabel('Emission Rate [kg CO$_2$/MWh]')
    ax_emiss.set_xlim(0, 8759)
    ax_emiss.set_ylim(0, 250)
    ax_emiss.legend(loc='upper right')

    if save:
        fig1.savefig(f"{savepath}eprice_hourly_Zeeland.pdf", format='pdf')
    plt.show()

    # === FIGURE 2: ECDF PLOTS WITH SWAPPED AXES ===
    fig2, axes2 = plt.subplots(1, 2, figsize=(6, 2.5), sharey=True)
    fig2.subplots_adjust(wspace=0.3, top=0.9, bottom=0.1, left=0.1, right=0.95)

    # ECDF Price
    ax_price_ecdf = axes2[0]
    for node, colors in zip(nodes, [colors_zeeland]):
        for i, year in enumerate(years):
            prices = data[node][year]['price'].sort_values()
            prob = np.linspace(0, 1, len(prices))
            ax_price_ecdf.plot(prob, prices, color=colors[i], label=f'{node} {labels[year]}', linewidth=0.8)
    ax_price_ecdf.set_title('Electricity Price')
    ax_price_ecdf.set_xlabel('Cumulative Probability')
    ax_price_ecdf.set_ylabel('Electricity Price [EUR/MWh]')
    ax_price_ecdf.set_xlim(0, 1)
    ax_price_ecdf.set_ylim(0, 200)
    ax_price_ecdf.legend(loc='upper left')

    # ECDF Emission
    ax_emiss_ecdf = axes2[1]
    for i, year in enumerate(years):
        emissions = data['Zeeland'][year]['emission'].sort_values()
        prob = np.linspace(0, 1, len(emissions))
        ax_emiss_ecdf.plot(prob, emissions, color=colors_emission[i],
                           linestyle='--', label=f'{labels[year]}', linewidth=0.8)
    ax_emiss_ecdf.set_title('Emission Rate')
    ax_emiss_ecdf.set_xlabel('Cumulative Probability')
    ax_emiss_ecdf.set_ylabel('Emission Rate [kg CO$_2$/MWh]')
    ax_emiss_ecdf.set_xlim(0, 1)
    ax_emiss_ecdf.set_ylim(0, 550)
    ax_emiss_ecdf.legend(loc='upper left')

    if save:
        fig2.savefig(f"{savepath}eprice_cumulative_dist.pdf", format='pdf')
    plt.show()


execute = 1

if execute == 1:
    # === PATHS & SETTINGS ===
    savepath = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/"
    el_load_path = Path("C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Case study data/IESA-Opt") / 'EU_electricity_prices.xlsx'
    save = 1

    # === YEARS & COLORS ===
    node = "EU"
    years = ['2022', '2030', '2040', '2050']
    labels = {'2022': '2022', '2030': '2030', '2040': '2040', '2050': '2050'}

    colors_zeeland = cm.devon(np.linspace(0, 0.8, len(years)))
    colors_emission = cm.grayC(np.linspace(0, 0.8, len(years)))

    # === LOAD DATA ===
    data = {node: {}}
    for year in years:
        el_importdata = pd.read_excel(el_load_path)
        data[node][year] = {
            'price': el_importdata.loc[:, int(year)]
        }


    # === MATPLOTLIB CONFIG ===
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "axes.labelsize": 10,
        "font.size": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })

    # === FIGURE 1: HOURLY PROFILES ===
    fig1, axes1 = plt.subplots(1, 1, figsize=(6, 2.5), sharex=True)
    fig1.subplots_adjust(hspace=0.4, top=0.85, bottom=0.1, left=0.1, right=0.98)

    # Top panel: Zeeland Price
    ax_price = axes1
    for i, year in enumerate(years):
        ax_price.plot(
            data[node][year]['price'],
            color=colors_zeeland[i],
            label=f"{labels[year]} ({data[node][year]['price'].mean():.1f} EUR/MWh)",
            linewidth=0.5
        )
    ax_price.set_title('Electricity Prices: EU')
    ax_price.set_ylabel('Electricity Price [EUR/MWh]')
    ax_price.set_xlim(0, 8759)
    ax_price.set_ylim(0, 550)
    ax_price.legend(loc='upper right')

    if save:
        fig1.savefig(f"{savepath}eprice_hourly_EU.pdf", format='pdf')
    plt.show()

    # === FIGURE 2: ECDF PLOTS WITH SWAPPED AXES ===
    fig2, axes2 = plt.subplots(1, 1, figsize=(2.5, 2.5), sharey=True)
    fig2.subplots_adjust(wspace=0.3, top=0.85, bottom=0.2, left=0.20, right=0.95)

    # ECDF Price
    ax_price_ecdf = axes2
    for i, year in enumerate(years):
        prices = data[node][year]['price'].sort_values()
        prob = np.linspace(0, 1, len(prices))
        ax_price_ecdf.plot(prob, prices, color=colors_zeeland[i], label=f'{node} {labels[year]}', linewidth=0.8)
    ax_price_ecdf.set_title('Electricity Price')
    ax_price_ecdf.set_xlabel('Cumulative Probability')
    ax_price_ecdf.set_ylabel('Electricity Price [EUR/MWh]')
    ax_price_ecdf.set_xlim(0, 1)
    ax_price_ecdf.set_ylim(0, 550)
    ax_price_ecdf.legend(loc='upper left')


    if save:
        fig2.savefig(f"{savepath}eprice_cumulative_dist_EU.pdf", format='pdf')
    plt.show()