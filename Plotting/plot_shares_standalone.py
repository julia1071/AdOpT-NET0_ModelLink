import os
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, gridspec

def plot_production_shares_stacked(df1, df2, categories, interpolation="spline", separate=1):
    plt.rcParams.update({'font.family': 'serif', 'font.size': 14})

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
                row['Conventional'] = 1
                row['Year'] = y
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        return df.sort_values('Year')

    df1 = fill_missing_years(df1, all_years)
    df2 = fill_missing_years(df2, all_years)

    def compute_shares(df):
        df_cat = df[[c for c in categories if c in df.columns]]
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
            x.append(2055)  # Add final point
            x = np.array(x)

            for col in shares.columns:
                y = np.append(shares[col].values, shares[col].values[-1])
                y_step = np.repeat(y, 2)[:-1]

                # Trim or pad y_step to match x
                if len(y_step) > len(x):
                    y_step = y_step[:len(x)]
                elif len(y_step) < len(x):
                    y_step = np.append(y_step, [y_step[-1]] * (len(x) - len(y_step)))

                y_interp = y_step.copy()

                for i in range(1, len(x), 2):
                    if x[i] - x[i - 1] == 1:
                        y0, y1 = y_step[i - 1], y_step[i]
                        t = np.linspace(0, 1, 2)
                        spline = make_interp_spline(t, [y0, y1], k=2)
                        y_interp[i - 1] = spline(0)
                        y_interp[i] = spline(1)

                interpolated[col] = y_interp

        else:
            raise ValueError(f"Unsupported interpolation method: {interpolation}")

        return x, interpolated

    if separate == 1:
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(7, 5.5), sharex=True,
                                       gridspec_kw={'hspace': 0.2}
                                       )

        for ax, df, label in zip((ax1, ax2), (df1, df2), ('ammonia', 'ethylene')):
            x, interpolated = interpolate(df, df['Year'].values)
            bottoms = np.zeros_like(x)
            for cat in categories:
                if cat in interpolated:
                    top = bottoms + interpolated[cat]
                    ax.fill_between(x, bottoms, top, color=categories[cat], label=cat)
                    bottoms = top
            ax.set_ylim(0, 1)
            ax.set_ylabel(f"Share of {label}")

        ax2.set_xticks([2025, 2030, 2040, 2050, 2055])
        ax2.set_xticklabels([r"Current", 2030, 2040, 2050, r"Post 2050"])
        ax2.set_xlim(x.min(), x.max())

        # # Combine legend from both axes
        # handles, labels = ax2.get_legend_handles_labels()
        # fig.legend(handles, labels,
        #            loc='lower center',
        #            bbox_to_anchor=(0.5, 0),
        #            ncol=2)
        # plt.subplots_adjust(bottom=0.4)

    else:
        # Merge and plot together
        merged = df1.copy()
        for cat in categories:
            merged[cat] = df1.get(cat, 0) + df2.get(cat, 0)
        merged = fill_missing_years(merged, all_years)
        x, interpolated = interpolate(merged, merged['Year'].values)

        fig, ax1 = plt.subplots(figsize=(7, 3))
        bottoms = np.zeros_like(x)
        for cat in categories:
            if cat in interpolated:
                top = bottoms + interpolated[cat]
                ax1.fill_between(x, bottoms, top, color=categories[cat], label=cat)
                bottoms = top
        ax1.set_ylabel("Share of Total Production")
        ax1.set_ylim(0, 1)
        ax1.set_xticks([2025, 2030, 2040, 2050, 2055])
        ax1.set_xticklabels([r"Current", 2030, 2040, 2050, r"Post 2050"])
        ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax1.set_title("Combined Production Shares")

    plt.tight_layout()


def save_separate_legend(categories, filename="legend.pdf"):

    plt.rcParams.update({'font.family': 'serif', 'font.size': 12})
    fig, ax = plt.subplots(figsize=(6.5, 0.6))  # Adjust width/height as needed

    # Create dummy handles
    handles = [mpatches.Patch(color=color, label=label)
               for label, color in categories.items()]

    # Add the legend to the figure
    legend = fig.legend(handles, categories.keys(),
                        loc='center',
                        ncol=4,  # adjust based on layout needs
                        frameon=False)

    ax.axis('off')  # Hide axes completely

    plt.tight_layout()
    fig.savefig(os.path.join("C:/Users/5637635/OneDrive - Universiteit Utrecht/Model Linking - shared/Figures/Python", f"{filename}"), format='pdf', bbox_inches='tight')
    plt.close(fig)



def main():
    flag_cluster_ambition = "Scope1-3"
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
        "Bio-based feedstock with CC": '#013220',
        "Plastic waste recycling": '#B475B2',
        "Plastic waste recycling with CC": '#533A8C',
    }

    combined_categories = {
        "Electrification + Bio-based feedstock": ("Electrification", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock": ("Conventional", "Bio-based feedstock"),
        "Conventional + Bio-based feedstock with CC": ("Conventional", "Bio-based feedstock with CC"),
    }


    production_sum_olefins = pd.read_excel(data_to_excel_path1, index_col=0, header=[0, 1])
    production_sum_ammonia = pd.read_excel(data_to_excel_path2, index_col=0, header=[0, 1])

    interpolation = "step"
    separate = 1

    df_plot_olefin = production_sum_olefins.loc[:, iterations].copy()
    df_plot_ammonia = production_sum_ammonia.loc[:, iterations].copy()
    plot_production_shares_stacked(df_plot_ammonia, df_plot_olefin, categories, interpolation=interpolation,
                                   separate=separate)

    # saving options
    save = "no"
    if save == "pdf":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
    elif save == "svg":
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')
    elif save == "both":
        plt.savefig(f"{plot_folder}.pdf", format='pdf', bbox_inches='tight')
        plt.savefig(f"{plot_folder}.svg", format='svg', bbox_inches='tight')

    plt.show()

    # # After all plots:
    # save_separate_legend(categories)

if __name__ == "__main__":
    main()
