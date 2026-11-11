from panda.generator import PANDA  

WINDOW_RES = [700, 700]
SELECTED_SPATIAL = 'CH'
SELECTED_SIZE = 'TA'           
SELECTED_DENSITY = 'numerical'  
MAX_N_IN_EXPERIMENT = 3
N_ANCHOR_VAL = 3               

optimal_params = PANDA.suggest_optimal_bases(
    window_res=WINDOW_RES,
    max_n=MAX_N_IN_EXPERIMENT,
    n_anchor=N_ANCHOR_VAL,
    spatial_type=SELECTED_SPATIAL,
    size_type=SELECTED_SIZE,
    density_type=SELECTED_DENSITY
)

print("=== PANDA Calculator ===")
print(f"Recomended base_cha: {optimal_params['base_cha']}")
print(f"Recomended base_ta: {optimal_params['base_ta']}")
if optimal_params['warning']:
    print(f"Warning: {optimal_params['warning']}")
print("======================================\n")
