import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from psychopy import core, visual

from panda.generator import PANDA


OUTPUT_BASE = "./output_stimuli"
WINDOW_RES = [700, 700]
N_RANGE = [3, 4, 5, 6, 7, 8]
REPETITIONS_PER_N = 10 
CONDITIONS = [
    ('CH', 'TA'),
    ('CH', 'TP'),
    ('ID', 'TA'),
    ('ID', 'TP'),
]

win = visual.Window(
    WINDOW_RES,
    color='white',
    units='pix',
    multiSample=True,
    numSamples=8,
)

gen = PANDA(
    win,
    n_anchor=3,
    base_ta=30000.0,
    base_cha=120000.0,
    color='black',
    seed=42,
)

print("Generating and validating dot arrays for various conditions and sizes...")

for spatial_type, size_type in CONDITIONS:
    cond_name = f"{spatial_type}_{size_type}"
    out_dir = os.path.join(OUTPUT_BASE, cond_name)
    os.makedirs(out_dir, exist_ok=True)

    for n in N_RANGE:
        for trial in range(1, REPETITIONS_PER_N + 1):
            img_path = os.path.join(
                out_dir, f"dot_N{n:02d}_{trial:03d}_{cond_name}.png"
            )
            try:
                gen.generate_and_save(
                    num_elements=n,
                    spatial_type=spatial_type,
                    size_type=size_type,
                    output_filepath=None,
                    sd_ratio=0.2,
                    save_results=False,
                    pause_time=0
                )
                
                gen.results[-1]['Condition'] = cond_name
                gen.results[-1]['Spatial_Type'] = spatial_type
                gen.results[-1]['Size_Type'] = size_type

            except Exception as e:
                print(f"Error [Condition: {cond_name}, N={n}, Trial={trial}]: {e}")

csv_path = os.path.join(OUTPUT_BASE, "results_validation.csv")
gen.save_csv(csv_path)
print(f"Zakończono. Wyniki zapisano do: {csv_path}")

win.close()

df = gen.get_dataframe()
print("Validation results saved to validation_results.csv")

print("\n" + "=" * 60)
print("Summary Statistics:")
print("=" * 60)


def cv(x):
    return (np.std(x) / np.mean(x)) * 100 if np.mean(x) != 0 else 0.0


stats_df = (
    df.groupby(['Condition', 'N'])
    .agg(
        TSA_Mean=('TSA', 'mean'),
        TSA_CV=('TSA', cv),
        TP_Mean=('TP', 'mean'),
        TP_CV=('TP', cv),
        CHA_Mean=('CHA', 'mean'),
        CHA_CV=('CHA', cv),
        ID_Mean=('ID', 'mean'),
        ID_CV=('ID', cv),
    )
    .round(2)
)

print(stats_df)
stats_df.to_csv("validation_summary_stats.csv")

sns.set_theme(style="whitegrid", font_scale=1.1)
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)

palette = {
    'CH_TA': '#1f77b4',
    'CH_TP': '#ff7f0e',
    'ID_TA': '#2ca02c',
    'ID_TP': '#d62728',
}

sns.lineplot(
    data=df,
    x='N',
    y='TSA',
    hue='Condition',
    style='Condition',
    markers=True,
    dashes=False,
    ax=axes[0, 0],
    palette=palette,
    err_style="bars",
)
axes[0, 0].set_title(
    "A. Total Surface Area (TSA)\n[Condition: *_TA]", fontsize=12
)
axes[0, 0].set_ylabel("TSA [px²]")

sns.lineplot(
    data=df,
    x='N',
    y='TP',
    hue='Condition',
    style='Condition',
    markers=True,
    dashes=False,
    ax=axes[0, 1],
    palette=palette,
    err_style="bars",
)
axes[0, 1].set_title(
    "B. Total Perimeter (TP)\n[Condition: *_TP]", fontsize=12
)
axes[0, 1].set_ylabel("TP [px]")

sns.lineplot(
    data=df,
    x='N',
    y='CHA',
    hue='Condition',
    style='Condition',
    markers=True,
    dashes=False,
    ax=axes[1, 0],
    palette=palette,
    err_style="bars",
)
axes[1, 0].set_title(
    "C. Convex Hull Area (CHA)\n[Condition: *_CHA]", fontsize=12
)
axes[1, 0].set_ylabel("CHA [px²]")
axes[1, 0].set_xlabel("Sample Size (N)")

sns.lineplot(
    data=df,
    x='N',
    y='ID',
    hue='Condition',
    style='Condition',
    markers=True,
    dashes=False,
    ax=axes[1, 1],
    palette=palette,
    err_style="bars",
)
axes[1, 1].set_title(
    "D. Mean Inter-individual Distance (ID)\n[Condition: *_ID]",
    fontsize=12,
)
axes[1, 1].set_ylabel("ID [px]")
axes[1, 1].set_xlabel("Sample Size (N)")

plt.suptitle(
    "Validation of Visual Feature Stability across Different Sample Sizes (N)",
    fontsize=14,
    fontweight='bold',
    y=0.98,
)
plt.tight_layout()
plt.subplots_adjust(top=0.90)

plt.savefig("validation_plots.png", dpi=300, bbox_inches='tight')
print("\nValidation plots saved to 'validation_plots.png'")
plt.show()

core.quit()