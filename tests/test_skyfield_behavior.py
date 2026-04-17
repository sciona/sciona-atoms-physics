from __future__ import annotations

import math

import numpy as np
import pytest

from sciona.atoms.physics.skyfield.atoms import (
    calculate_vector_angle,
    compute_spherical_coordinate_rates,
)


def test_calculate_vector_angle_matches_right_angle_case() -> None:
    angle = calculate_vector_angle(np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]))
    assert angle == pytest.approx(math.pi / 2.0)


def test_compute_spherical_coordinate_rates_exposes_upstream_six_tuple() -> None:
    result = compute_spherical_coordinate_rates(
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    )

    assert result == pytest.approx((1.0, 0.0, 0.0, 0.0, 0.0, 1.0))
