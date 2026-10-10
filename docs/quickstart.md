# Quick start

## Installation

You can install the package directly from PyPI:

```bash
pip install panda-generator
```

## Basic Usage
The following example demonstrates how to initialize PANDA, generate stimulus images for different conditions, and save the metadata to a CSV file:

```python
import os
from psychopy import core, visual
from panda.generator import PANDA

WINDOW_RES = [700, 700]
OUTPUT_BASE = 'output_path'

CONDITIONS = [('ID', 'TA'), ('ID', 'TP')]
N_COUNTS = {2: 4, 3: 6, 4: 2, 5: 4}

win = visual.Window(
    WINDOW_RES, color='black', units='pix', multiSample=True, numSamples=8
)

gen = PANDA(
    win, n_anchor=3, base_ta=30000, base_cha=120000, color='white', seed=42
)

for spatial_type, size_type in CONDITIONS:
    condition_name = f'{spatial_type}_{size_type}'
    out_dir = os.path.join(OUTPUT_BASE, condition_name)
    os.makedirs(out_dir, exist_ok=True)

    print(f'Generating: {condition_name}')

    for n_val, count in N_COUNTS.items():
        for i in range(1, count + 1):
            img_path = os.path.join(
                out_dir, f'dot_N{n_val:02d}_{i:03d}_{condition_name}.png'
            )
            try:
                gen.generate_and_save(
                    num_elements=n_val,
                    spatial_type=spatial_type,
                    size_type=size_type,
                    output_filepath=img_path,
                    sd_ratio=0.2,
                    save_results=True,
                    pause_time=0
                )
            except Exception as e:
                print(f'Error [N={n_val}, attempt {i}]: {e}')

    gen.save_csv(os.path.join(out_dir, f'results_{condition_name}.csv'))

win.close()
core.quit()
```