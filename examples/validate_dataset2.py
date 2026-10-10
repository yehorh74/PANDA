import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from psychopy import core, visual

from panda.generator import PANDA

OUTPUT_BASE = "./output_stimuli"
EXCEL_PATH = os.path.join(OUTPUT_BASE, "validation_report2.xlsx")
WINDOW_RES = [700, 700]
N_RANGE = [10]
REPETITIONS_PER_N = 100  
CONDITIONS = [
    ('CH', 'TA'),
    ('CH', 'TP'),
    ('ID', 'TA'),
    ('ID', 'TP'),
]

BASE_TA = 30000.0
BASE_CHA = 120000.0
N_ANCHOR = 10
MEAN_R_ANCHOR = np.sqrt((BASE_TA / N_ANCHOR) / np.pi)
BASE_TP = N_ANCHOR * (2 * np.pi * MEAN_R_ANCHOR)  # ~1059.53 px
BASE_ID = (0.51 * np.sqrt(BASE_CHA)) + (2 * MEAN_R_ANCHOR)  # ~289.51 px

win = visual.Window(
    WINDOW_RES,
    color='white',
    units='pix',
    multiSample=True,
    numSamples=8,
)

gen = PANDA(
    win,
    n_anchor=N_ANCHOR,
    base_ta=BASE_TA,
    base_cha=BASE_CHA,
    color='black',
    seed=42,
)

print(f"Generating and validating stimuli ({REPETITIONS_PER_N} trials per N)...")

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
                    pause_time=0,
                )

                gen.results[-1]['Condition'] = cond_name
                gen.results[-1]['Spatial_Type'] = spatial_type
                gen.results[-1]['Size_Type'] = size_type
                gen.results[-1]['Trial'] = trial

            except Exception as e:
                print(f"Error [Condition: {cond_name}, N={n}, Trial={trial}]: {e}")

win.close()  

df = gen.get_dataframe()

def sem(x):
    return np.std(x, ddof=1) / np.sqrt(len(x))


def cv(x):
    m = np.mean(x)
    return (np.std(x, ddof=1) / m) * 100 if m != 0 else 0.0


stats_df = (
    df.groupby(['Condition', 'N'])
    .agg(
        # TSA
        TSA_Mean=('TSA', 'mean'),
        TSA_SD=('TSA', lambda x: np.std(x, ddof=1)),
        TSA_SEM=('TSA', sem),
        TSA_CV=('TSA', cv),
        # TP
        TP_Mean=('TP', 'mean'),
        TP_SD=('TP', lambda x: np.std(x, ddof=1)),
        TP_SEM=('TP', sem),
        TP_CV=('TP', cv),
        # CHA
        CHA_Mean=('CHA', 'mean'),
        CHA_SD=('CHA', lambda x: np.std(x, ddof=1)),
        CHA_SEM=('CHA', sem),
        CHA_CV=('CHA', cv),
        # ID
        ID_Mean=('ID', 'mean'),
        ID_SD=('ID', lambda x: np.std(x, ddof=1)),
        ID_SEM=('ID', sem),
        ID_CV=('ID', cv),
    )
    .reset_index()
)

def get_target(row, feature):
    if feature == 'TSA' and row['Size_Type'] == 'TA':
        return BASE_TA
    if feature == 'TP' and row['Size_Type'] == 'TP':
        return BASE_TP
    if feature == 'CHA' and row['Spatial_Type'] == 'CH':
        return BASE_CHA
    if feature == 'ID' and row['Spatial_Type'] == 'ID':
        return BASE_ID
    return np.nan


errors = []
for idx, row in df.iterrows():
    target_tsa = BASE_TA if row['Size_Type'] == 'TA' else np.nan
    target_tp = BASE_TP if row['Size_Type'] == 'TP' else np.nan
    target_cha = BASE_CHA if row['Spatial_Type'] == 'CH' else np.nan
    target_id = BASE_ID if row['Spatial_Type'] == 'ID' else np.nan

    errors.append({
        'Trial_ID': idx,
        'TSA_Abs_Error': abs(row['TSA'] - target_tsa),
        'TSA_Rel_Error_%': (abs(row['TSA'] - target_tsa) / target_tsa) * 100 if pd.notna(target_tsa) else np.nan,
        'TP_Abs_Error': abs(row['TP'] - target_tp),
        'TP_Rel_Error_%': (abs(row['TP'] - target_tp) / target_tp) * 100 if pd.notna(target_tp) else np.nan,
        'CHA_Abs_Error': abs(row['CHA'] - target_cha),
        'CHA_Rel_Error_%': (abs(row['CHA'] - target_cha) / target_cha) * 100 if pd.notna(target_cha) else np.nan,
        'ID_Abs_Error': abs(row['ID'] - target_id),
        'ID_Rel_Error_%': (abs(row['ID'] - target_id) / target_id) * 100 if pd.notna(target_id) else np.nan,
    })

error_df = pd.DataFrame(errors)
df_with_errors = pd.concat([df, error_df.drop(columns=['Trial_ID'])], axis=1)

reliability_results = []

for cond in df['Condition'].unique():
    cond_data = df[df['Condition'] == cond]

    for n in N_RANGE:
        sub = cond_data[cond_data['N'] == n].sort_values('Trial')

        if 'TA' in cond:
            metric = 'TSA'
        else:
            metric = 'TP'

        if 'CH' in cond:
            spatial_metric = 'CHA'
        else:
            spatial_metric = 'ID'

        for m_name, m_col in [('Size_Feature', metric), ('Spatial_Feature', spatial_metric)]:
            vals = sub[m_col].values

            # Split-Half Reliability
            odd_trials = vals[0::2]  
            even_trials = vals[1::2]  

            if np.std(odd_trials) == 0 or np.std(even_trials) == 0:
                r_split = 1.0  
                r_spearman_brown = 1.0
            else:
                r_split, _ = stats.pearsonr(odd_trials, even_trials)
                r_spearman_brown = (2 * r_split) / (1 + r_split)

            # Test-Retest
            first_half = vals[:50]
            second_half = vals[50:]

            if np.std(first_half) == 0 or np.std(second_half) == 0:
                r_retest = 1.0
            else:
                r_retest, _ = stats.pearsonr(first_half, second_half)

            t_stat, p_val_diff = stats.ttest_rel(first_half, second_half)

            reliability_results.append({
                'Condition': cond,
                'N': n,
                'Feature_Type': m_name,
                'Metric': m_col,
                'SplitHalf_r': round(r_split, 4),
                'SpearmanBrown_Reliability': round(r_spearman_brown, 4),
                'TestRetest_r': round(r_retest, 4),
                'Stability_t_stat': round(t_stat, 4) if pd.notna(t_stat) else 0.0,
                'Stability_p_value': round(p_val_diff, 4) if pd.notna(p_val_diff) else 1.0,
            })

reliability_df = pd.DataFrame(reliability_results)

print(f"\nReliability analysis saved to: {EXCEL_PATH}")
with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
    df_with_errors.to_excel(writer, sheet_name='Raw_Data_And_Errors', index=False)
    stats_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
    reliability_df.to_excel(writer, sheet_name='Reliability_Analysis', index=False)

print("Reliability analysis has been saved successfully.")

sns.set_theme(style="whitegrid", font_scale=1.1)
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)

palette = {
    'CH_TA': '#1f77b4',
    'CH_TP': '#ff7f0e',
    'ID_TA': '#2ca02c',
    'ID_TP': '#d62728',
}

# A. TSA
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
    errorbar="se",
)
axes[0, 0].set_title("A. Total Surface Area (TSA)\n[Controlled in *_TA]", fontsize=12)
axes[0, 0].set_ylabel("TSA [px²]")

# B. TP
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
    errorbar="se",
)
axes[0, 1].set_title("B. Total Perimeter (TP)\n[Controlled in *_TP]", fontsize=12)
axes[0, 1].set_ylabel("TP [px]")

# C. CHA
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
    errorbar="se",
)
axes[1, 0].set_title("C. Convex Hull Area (CHA)\n[Controlled in CH_*]", fontsize=12)
axes[1, 0].set_ylabel("CHA [px²]")
axes[1, 0].set_xlabel("Sample Size (N)")

# D. ID
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
    errorbar="se",
)
axes[1, 1].set_title("D. Mean Inter-individual Distance (ID)\n[Controlled in ID_*]", fontsize=12)
axes[1, 1].set_ylabel("ID [px]")
axes[1, 1].set_xlabel("Sample Size (N)")

plt.suptitle(
    f"Validation of Visual Feature Control & Stability (N_trials={REPETITIONS_PER_N} per condition)",
    fontsize=14,
    fontweight='bold',
    y=0.98,
)
plt.tight_layout()
plt.subplots_adjust(top=0.90)

plot_path = os.path.join(OUTPUT_BASE, "validation_plots2.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"Validation plots saved to: {plot_path}")

plt.show()
core.quit()