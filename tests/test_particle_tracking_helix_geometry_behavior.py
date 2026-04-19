from __future__ import annotations

import numpy as np


def test_all_five_atoms_import() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import (
        circle_from_three_points,
        helix_direction_from_two_points,
        helix_nearest_point_distance,
        helix_pitch_from_two_points,
        helix_pitch_least_squares,
    )
    assert callable(circle_from_three_points)
    assert callable(helix_pitch_from_two_points)
    assert callable(helix_pitch_least_squares)
    assert callable(helix_direction_from_two_points)
    assert callable(helix_nearest_point_distance)


def _helix_points(
    n: int, xm: float = 1.0, ym: float = 0.0, r: float = 1.0, pitch: float = 5.0
) -> tuple[np.ndarray, ...]:
    """Generate 3 points per helix on N known helices."""
    t = np.linspace(0, np.pi / 2, 3 * n).reshape(n, 3).T
    x = xm + r * np.cos(t)
    y = ym + r * np.sin(t)
    z = pitch / (2 * np.pi) * t
    return x, y, z


def test_circle_fit_recovers_known_radius() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import circle_from_three_points

    x, y, z = _helix_points(20)
    xm, ym, r = circle_from_three_points(x[0], y[0], x[1], y[1], x[2], y[2])
    assert np.allclose(r, 1.0, atol=1e-10)


def test_circle_fit_handles_collinear_points() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import circle_from_three_points

    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 0.0, 0.0])
    xm, ym, r = circle_from_three_points(x, y, x, y, x, y)
    assert np.all(np.isfinite(r))
    assert np.all(r > 0)


def test_pitch_from_two_points_recovers_known_pitch() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import (
        circle_from_three_points,
        helix_pitch_from_two_points,
    )

    x, y, z = _helix_points(20)
    xm, ym, r = circle_from_three_points(x[0], y[0], x[1], y[1], x[2], y[2])
    pitch, phid, dz = helix_pitch_from_two_points(
        x[0], y[0], z[0], x[1], y[1], z[1], xm, ym
    )
    assert np.allclose(pitch, 5.0, atol=1e-6)


def test_pitch_least_squares_has_zero_loss_on_exact_helix() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import (
        circle_from_three_points,
        helix_pitch_least_squares,
    )

    x, y, z = _helix_points(20)
    xm, ym, r = circle_from_three_points(x[0], y[0], x[1], y[1], x[2], y[2])
    pitch, phid, dz, loss = helix_pitch_least_squares(
        x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2], xm, ym
    )
    assert np.allclose(pitch, 5.0, atol=1e-6)
    assert np.allclose(loss, 0.0, atol=1e-20)


def test_nearest_point_distance_near_zero_for_on_helix_point() -> None:
    from sciona.atoms.particle_tracking.helix_geometry.atoms import (
        circle_from_three_points,
        helix_nearest_point_distance,
        helix_pitch_from_two_points,
    )

    x, y, z = _helix_points(20)
    xm, ym, r = circle_from_three_points(x[0], y[0], x[1], y[1], x[2], y[2])
    pitch, _, _ = helix_pitch_from_two_points(
        x[0], y[0], z[0], x[1], y[1], z[1], xm, ym
    )
    # Query the second point — should be distance ~0
    x1, y1, z1, dist = helix_nearest_point_distance(
        x[0], y[0], z[0], xm, ym, r, pitch, x[1], y[1], z[1]
    )
    assert np.all(dist < 1e-6)
