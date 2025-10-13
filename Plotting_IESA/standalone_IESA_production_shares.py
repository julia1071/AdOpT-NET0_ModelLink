import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ================= SETTINGS =================
scope3 = 1
if scope3:
    file = r"C:\Users\5637635\OneDrive - Universiteit Utrecht\Model Linking - shared\Results\Final\250911_standalone_scope1-3\ResultsModelLinking_General_standalone.xlsx"
    ext = "_scope3"
else:
    file = r"C:\Users\5637635\OneDrive - Universiteit Utrecht\Model Linking - shared\Results\Final\250902_standalone_BaU\ResultsModelLinking_General_standalone.xlsx"
    ext = ""

sheet = "SupplyDemand"
years_discrete = ["2022", "2030", "2040", "2050"]
years_cont = np.arange(2022, 2056)
plot_folder = r"C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures_IESA/"
save = "both"  # options: "no", "pdf", "svg", "both"

# =============== CATEGORIES =================
categories = {
    "Imports": "black",
    "Conventional": '#8C8B8B',
    "Carbon Capture": '#3E7EB0',
    "Electrification": '#E9E46D',
    "Water electrolysis": '#EABF37',
    r"CO$_2$ utilization": '#E18826',
    "Bio-based feedstock": '#84AA6F',
    "Bio-based feedstock with CC": '#088A01',
    "Plastic waste recycling": '#B475B2',
    "Plastic waste recycling with CC": '#533A8C'
}

combined_categories = {
    "Electrification + Bio-based feedstock": ("Electrification", "Bio-based feedstock"),
    "Conventional + Bio-based feedstock": ("Conventional", "Bio-based feedstock"),
    "Conventional + Bio-based feedstock with CC": ("Carbon Capture", "Bio-based feedstock with CC"),
}

# ================= TECHNOLOGY MAPPINGS =================
ammonia_mapping = {
    'Amm01_01': 'Conventional',
    'Amm01_02': 'Carbon Capture',
    'Amm01_08': 'Electrification',
    'Amm01_05': 'Water electrolysis',
}

olefins_mapping = {
    'ICH01_16': 'Imports',  # include in plot, no legend
    'ICH01_01': 'Conventional',
    'ICH01_14': 'Conventional',
    'ICH01_02': 'Carbon Capture',
    'ICH01_42': 'Conventional + Bio-based feedstock',
    'ICH01_03': 'Conventional + Bio-based feedstock with CC',
    'ICH01_05': 'Electrification',
    'ICH01_12': 'Electrification',
    'ICH01_11': 'Bio-based feedstock',
    'ICH01_41': 'Bio-based feedstock',
    'ICH01_40': r"CO$_2$ utilization",
}

# ================= HELPER FUNCTIONS =================
def preprocess_df(df, activity_filter):
    # Strip column names
    df.columns = df.columns.astype(str).str.strip()

    # Filter for the activity and supply type
    df_filtered = df[
        (df['Activity'].str.contains(activity_filter, case=False, na=False)) &
        (df['Type'].str.strip().str.lower() == 'supply')
    ]

    # Identify year columns
    year_cols = [col for col in df_filtered.columns if col.isdigit()]

    # Sum over duplicate Tech_IDs per year
    df_summed = df_filtered.groupby('Tech_ID')[year_cols].sum()

    return df_summed


def interpolate(df, years_cont):
    # Identify only the year columns
    year_cols = df.columns
    years = np.array(list(map(int, year_cols)))

    # Prepare output DataFrame
    df_interp = pd.DataFrame(index=df.index, columns=years_cont, dtype=float)

    for tech in df.index:
        vals = df.loc[tech, year_cols].astype(float).values.flatten()

        # Linear interpolation
        df_interp.loc[tech] = np.interp(years_cont, years, vals)

    return df_interp


def map_to_categories(df, mapping):
    df_cat = pd.DataFrame(index=df.index, columns=df.columns)
    for tech in df.index:
        cat = mapping.get(tech, None)
        if cat is not None:
            df_cat.loc[tech] = cat
    return df_cat

# ================= LOAD DATA =================
df = pd.read_excel(file, sheet_name=sheet)

# Ammonia
ammonia_df = preprocess_df(df, 'Ammonia')
ammonia_interp = interpolate(ammonia_df, years_cont)

# Olefins (ethylene + propylene)
olefins_df = preprocess_df(df, 'ethylene|propylene')
olefins_interp = interpolate(olefins_df, years_cont)

# ================= AGGREGATE BY CATEGORY =================
def aggregate_categories(df_interp, mapping, categories, combined_categories):
    df_cat = pd.DataFrame(0.0, index=list(categories.keys()) + list(combined_categories.keys()),
                          columns=df_interp.columns, dtype=float)
    for tech in df_interp.index:
        cat = mapping.get(tech, None)
        if cat is None:
            continue
        # if cat in combined_categories:
        #     # Skip for now, combined will be plotted with hatch
        #     continue
        df_cat.loc[cat] += df_interp.loc[tech]
    return df_cat

ammonia_cat = aggregate_categories(ammonia_interp, ammonia_mapping, categories, combined_categories)
olefins_cat = aggregate_categories(olefins_interp, olefins_mapping, categories, combined_categories)

# ================= PLOT =================
def step_interpolate(df_cat, years_cont):
    """Step-wise interpolation: flat until year-1, then jump to next level."""
    interpolated = pd.DataFrame(index=df_cat.index, columns=years_cont, dtype=float)
    # years_orig = df_cat.columns.astype(int)
    years_orig = [2022, 2030, 2040, 2050]

    for cat in df_cat.index:
        y_step = np.zeros(len(years_cont))
        # Go through intervals between original years
        for i in range(len(years_orig)-1):
            start_year = years_orig[i]
            end_year = years_orig[i+1] - 1  # flat until year before next
            mask = (years_cont >= start_year) & (years_cont <= end_year)
            y_step[mask] = df_cat.loc[cat, years_orig[i]]
        # Last interval: flat until last year in years_cont
        mask = years_cont >= years_orig[-1]
        y_step[mask] = df_cat.loc[cat, years_orig[-1]]
        interpolated.loc[cat] = y_step

    return interpolated

def plot_area(ax, x, interpolated, label, bottom, color=None, hatch=None, edgecolor=None):
    top = bottom + interpolated
    ax.fill_between(x, bottom, top, facecolor=color, edgecolor=edgecolor or "black",
                    hatch=hatch, linewidth=0.0, label=label)
    return top

def plot_shares(ammonia_cat, olefins_cat, categories, combined_categories, plotting_order, years_cont):
    plt.rcParams.update({'font.family': 'serif', 'font.size': 14})
    # Compute shares per year
    ammonia_share = ammonia_cat.div(ammonia_cat.sum(axis=0), axis=1)
    olefins_share = olefins_cat.div(olefins_cat.sum(axis=0), axis=1)

    # Step-wise interpolation
    ammonia_interp = step_interpolate(ammonia_share, years_cont)
    olefins_interp = step_interpolate(olefins_share, years_cont)

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(8, 6), sharex=True,
                                   gridspec_kw={'hspace':0.2})

    for ax, df_interp, label in zip([ax1, ax2], [ammonia_interp, olefins_interp], ['ammonia', 'olefins']):
        bottoms = np.zeros(len(years_cont))
        x = years_cont

        for cat in plotting_order:
            if cat not in df_interp.index:
                continue
            interpolated = df_interp.loc[cat].values
            if cat in combined_categories:
                base1, base2 = combined_categories[cat]
                bottoms = plot_area(ax, x, interpolated, cat, bottoms,
                                    color=categories[base1],
                                    hatch='////',
                                    edgecolor=categories[base2])
            else:
                bottoms = plot_area(ax, x, interpolated, cat, bottoms,
                                    color=categories[cat])

        ax.set_ylim(0,1)
        ax.set_ylabel(f"Share of {label} \n production", fontsize=16)
        ax.set_xticks([2022, 2030, 2040, 2050, 2055])
        ax.set_xticklabels([2022, 2030, 2040, 2050, r"Post 2050"], fontsize=16)
        ax.set_xlim(x.min(), x.max())
        ax.tick_params(axis='y', labelsize=14)

    # Legend
    # handles, labels = ax1.get_legend_handles_labels()
    # fig.legend(handles, labels, loc='lower center', ncol=5, fontsize='small', frameon=False)
    plt.tight_layout(rect=[0,0.12,1,1])

    return fig, (ax1, ax2)

# ================= PLOT CALL =================
plotting_order = list(categories.keys()) + list(combined_categories.keys())
fig, axes = plot_shares(ammonia_cat, olefins_cat, categories, combined_categories, plotting_order, years_cont)



# =============== SAVE =================
if save in ["pdf", "both"]:
    fig.savefig(f"{plot_folder}/national_production_shares{ext}.pdf", bbox_inches='tight', format='pdf')
if save in ["svg", "both"]:
    fig.savefig(f"{plot_folder}/national_production_shares{ext}.svg", bbox_inches='tight', format='svg')

plt.show()
