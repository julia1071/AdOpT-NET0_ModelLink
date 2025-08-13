import os
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, gridspec

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.interpolate import make_interp_spline

def plot_production_shares_stacked(df1, df2, categories, combined_categories=None, interpolation="spline", separate=1):
    plt.rcParams.update({'font.family': 'serif', 'font.size': 14})

    if combined_categories is None:
        combined_categories = {}

    def preprocess(df):
        df.columns.name = None
        df = df.T.reset_index()
        df = df.rename(columns={'index': 'Year'})
        df['Year'] = df['Interval'].astype(int)
        return df

    df1 = preprocess(df1)
    df2 = preprocess(df2)

    all_years = sorted(set(df1['Year']) | set(df2['Year']) | {2025})

    def fill_missing_years(df, years):
        for y in years:
            if y not in df['Year'].values:
                row = {cat: 0 for cat in categories}
                row.update({cat: 0 for cat in combined_categories})
                row['Conventional'] = 1  # default fallback
                row['Year'] = y
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        return df.sort_values('Year')

    df1 = fill_missing_years(df1, all_years)
    df2 = fill_missing_years(df2, all_years)

    def compute_shares(df):
        df_cat = df[[c for c in df.columns if c not in ['Iteration', 'Year', 'Interval']]]
        return df_cat.div(df_cat.sum(axis=1), axis=0)

    def interpolate(df, years):
        shares = compute_shares(df)
        if interpolation == "spline":
            x = np.linspace(min(years), max(years), 300)
            interpolated = {
                col: make_interp_spline(years, shares[col], k=2)(x)
                for col in shares.columns
            }
        elif interpolation == "linear":
            x = np.array(years)
            interpolated = {
                col: np.interp(x, years, shares[col])
                for col in shares.columns
            }
        elif interpolation == "step":
            interpolated = {}
            x = []
            for i, year in enumerate(years):
                if i == 0:
                    x.append(year)
                else:
                    x.extend([year - 1, year])
            x.append(2055)
            x = np.array(x)
            for col in shares.columns:
                y = np.append(shares[col].values, shares[col].values[-1])
                y_step = np.repeat(y, 2)[:-1]
                if len(y_step) > len(x):
                    y_step = y_step[:len(x)]
                elif len(y_step) < len(x):
                    y_step = np.append(y_step, [y_step[-1]] * (len(x) - len(y_step)))
                interpolated[col] = y_step
        else:
            raise ValueError(f"Unsupported interpolation method: {interpolation}")

        return x, interpolated

    def plot_area(ax, x, interpolated, label, bottom, color=None, hatch=None, edgecolor=None):
        top = bottom + interpolated
        ax.fill_between(x, bottom, top, facecolor=color, edgecolor=edgecolor or "black", hatch=hatch, linewidth=0.0, label=label)
        return top

    if separate == 1:
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(7, 5.5), sharex=True,
                                       gridspec_kw={'hspace': 0.2})

        for ax, df, label in zip((ax1, ax2), (df1, df2), ('ammonia', 'ethylene')):
            x, interpolated = interpolate(df, df['Year'].values)
            bottoms = np.zeros_like(x)

            for cat in list(categories) + list(combined_categories):
                if cat not in interpolated:
                    continue
                if cat in combined_categories:
                    base1, base2 = combined_categories[cat]
                    bottoms = plot_area(ax, x, interpolated[cat], cat,
                                        bottoms,
                                        color=categories[base1],
                                        hatch='////',
                                        edgecolor=categories[base2])
                else:
                    bottoms = plot_area(ax, x, interpolated[cat], cat,
                                        bottoms,
                                        color=categories[cat])

            ax.set_ylim(0, 1)
            ax.set_ylabel(f"Share of {label}")

        ax2.set_xticks([2025, 2030, 2040, 2050, 2055])
        ax2.set_xticklabels([r"Current", 2030, 2040, 2050, r"Post 2050"])
        ax2.set_xlim(x.min(), x.max())

    else:
        # Combine both into one
        merged = df1.copy()
        for cat in df2.columns:
            if cat not in merged:
                merged[cat] = 0
            merged[cat] += df2.get(cat, 0)
        merged = fill_missing_years(merged, all_years)
        x, interpolated = interpolate(merged, merged['Year'].values)

        fig, ax1 = plt.subplots(figsize=(7, 3))
        bottoms = np.zeros_like(x)
        for cat in list(categories) + list(combined_categories):
            if cat not in interpolated:
                continue
            if cat in combined_categories:
                base1, base2 = combined_categories[cat]
                bottoms = plot_area(ax1, x, interpolated[cat], cat,
                                    bottoms,
                                    color=categories[base1],
                                    hatch='///',
                                    edgecolor=categories[base2])
            else:
                bottoms = plot_area(ax1, x, interpolated[cat], cat,
                                    bottoms,
                                    color=categories[cat])

        ax1.set_ylabel("Share of Total Production")
        ax1.set_ylim(0, 1)
        ax1.set_xticks([2025, 2030, 2040, 2050, 2055])
        ax1.set_xticklabels([r"Current", 2030, 2040, 2050, r"Post 2050"])
        ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax1.set_title("Combined Production Shares")

    plt.tight_layout()



def save_separate_legend(categories, combined_categories, filename="legend"):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    plt.rcParams.update({'font.family': 'serif', 'font.size': 12})
    fig, ax = plt.subplots(figsize=(7.5, 1))  # Adjust as needed

    handles = [mpatches.Patch(color=color, label=label)
               for label, color in categories.items()]

    for label, (base1, base2) in combined_categories.items():
        handles.append(
            mpatches.Patch(facecolor=categories[base1],
                           edgecolor=categories[base2],
                           hatch='///',
                           label=label)
        )

    ax.axis('off')
    legend = fig.legend(handles=handles,
                        loc='center',
                        ncol=4,
                        frameon=False)

    plt.tight_layout()
    fig.savefig(os.path.join("C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python",
                             f"{filename}.pdf"), format='pdf', bbox_inches='tight')
    fig.savefig(os.path.join("C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python",
                             f"{filename}.svg"), format='svg', bbox_inches='tight')
    plt.close(fig)




def main():
    flag_cluster_ambition = "LowAmbition"
    iterations = ['Standalone']

    # Add basepath
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_to_excel_path1 = os.path.join(datapath, "Plotting", f"production_shares_olefins_{flag_cluster_ambition}.xlsx")
    data_to_excel_path2 = os.path.join(datapath, "Plotting", f"production_shares_ammonia_{flag_cluster_ambition}.xlsx")
    plot_folder = "C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python/ProdShares_" + flag_cluster_ambition

    categories = {
        "Conventional": '#8C8B8B',
        "Carbon Capture": '#3E7EB0',
        "Electrification": '#E9E46D',
        "Water electrolysis": '#EABF37',
        r"CO$_2$ utilization": '#E18826',
        "Bio-based feedstock": '#84AA6F',
        "Bio-based feedstock with CC": '#088A01',
        "Plastic waste recycling": '#B475B2',
        "Plastic waste recycling with CC": '#533A8C',
    }

    combined_categories = {
        "Electrification + Bio-based feedstock": ("Electrification", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock": ("Conventional", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock with CC": ("Carbon Capture", "Bio-based feedstock with CC"),
    }


    production_sum_olefins = pd.read_excel(data_to_excel_path1, index_col=0, header=[0, 1])
    production_sum_ammonia = pd.read_excel(data_to_excel_path2, index_col=0, header=[0, 1])

    interpolation = "step"
    separate = 1

    df_plot_olefin = production_sum_olefins.loc[:, iterations].copy()
    df_plot_ammonia = production_sum_ammonia.loc[:, iterations].copy()

    plot_production_shares_stacked(df_plot_ammonia, df_plot_olefin,
                                   categories,
                                   combined_categories,
                                   interpolation=interpolation,
                                   separate=separate)

    # saving options
    save = "both"
    if save == "pdf":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    elif save == "svg":
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
    elif save == "both":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')

    plt.show()

    # After all plots:
    # save_separate_legend(categories, combined_categories)

if __name__ == "__main__":
    main()
