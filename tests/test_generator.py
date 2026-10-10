import pytest
import numpy as np


@pytest.mark.parametrize("spatial_type, size_type", [
    ('CH', 'TA'),
    ('CH', 'TP'),
    ('ID', 'TA'),
    ('ID', 'TP'),
])
def test_generate_balanced_set_dimensions(panda_instance, spatial_type, size_type):
    num_elements = 6
    dots, radii, pos = panda_instance.generate_balanced_set(
        num_elements=num_elements,
        spatial_type=spatial_type,
        size_type=size_type,
        sd_ratio=0.2,
        min_dist_factor=2.0,
    )

    assert len(radii) == num_elements
    assert len(pos) == num_elements
    assert all(len(p) == 2 for p in pos)


def test_log_ground_truth(panda_instance):
    num_elements = 4
    radii = np.array([10.0, 10.0, 10.0, 10.0])
    pos = np.array([[0, 0], [50, 0], [50, 50], [0, 50]])

    panda_instance.reset_results()
    metrics = panda_instance.log_ground_truth(num_elements, radii, pos)

    assert len(panda_instance.results) == 1
    assert metrics['N'] == num_elements
    assert np.isclose(metrics['TSA'], 4 * np.pi * 100)
    assert metrics['CHA'] == 2500.0  