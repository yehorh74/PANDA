import numpy as np
import pytest


def test_compute_convex_hull_area(panda_instance):
    square_positions = np.array([
        [0, 0],
        [100, 0],
        [100, 100],
        [0, 100]
    ])
    area = panda_instance._compute_convex_hull_area(square_positions)
    assert np.isclose(area, 10000.0)


def test_get_radii_total_surface_area(panda_instance):
    target_ta = 30000.0
    num_elements = 5
    sd_ratio = 0.2

    radii = panda_instance._get_radii(num_elements, target_ta, sd_ratio)
    calculated_ta = np.sum(np.pi * (radii ** 2))

    assert len(radii) == num_elements
    assert np.isclose(calculated_ta, target_ta)
