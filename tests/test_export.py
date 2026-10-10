import os
import pandas as pd


def test_dataframe_and_csv_export(panda_instance, tmp_path):
    panda_instance.reset_results()

    _, radii, pos = panda_instance.generate_balanced_set(5, 'CH', 'TA')
    panda_instance.log_ground_truth(5, radii, pos)

    df = panda_instance.get_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert 'TSA' in df.columns
    assert 'CHA' in df.columns

    csv_file = tmp_path / "test_output.csv"
    panda_instance.save_csv(str(csv_file))

    assert os.path.exists(csv_file)
    loaded_df = pd.read_csv(csv_file)
    assert len(loaded_df) == 1