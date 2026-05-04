from __future__ import annotations

import numpy as np
import sympy as sp

from sciona.ghost.registry import REGISTRY


def test_all_three_atoms_import() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import (
        coordinate_rescaling_for_knn,
        perturbative_cap_correction,
        perturbative_cylinder_correction,
    )
    assert callable(coordinate_rescaling_for_knn)
    assert callable(perturbative_cap_correction)
    assert callable(perturbative_cylinder_correction)


def test_coordinate_rescaling_output_shape() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import coordinate_rescaling_for_knn

    rng = np.random.default_rng(42)
    coords = rng.normal(size=(10, 3)) * 100.0
    coords[:, 0] += 50.0  # avoid zero radius

    result = coordinate_rescaling_for_knn(coords, cyl_mean_r2=200.0, z_scale=5.0)
    assert result.shape == (10, 3)
    assert np.all(np.isfinite(result))


def test_coordinate_rescaling_projects_to_reference_radius() -> None:
    """After rescaling (with z_scale=1), xy-norm should be cyl_mean_r2."""
    from sciona.atoms.particle_tracking.detector_corrections.atoms import coordinate_rescaling_for_knn

    coords = np.array([
        [100.0, 0.0, 50.0],
        [0.0, 200.0, -30.0],
        [50.0, 50.0, 100.0],
    ])
    cyl_mean_r2 = 150.0

    # With z_scale=1, x' = x * (r_mean/r) * 1 and y' = y * (r_mean/r) * 1
    result = coordinate_rescaling_for_knn(coords, cyl_mean_r2=cyl_mean_r2, z_scale=1.0)
    xy_norm = np.sqrt(np.square(result[:, 0]) + np.square(result[:, 1]))
    assert np.allclose(xy_norm, cyl_mean_r2, rtol=1e-10)


def test_coordinate_rescaling_z_scale_affects_xy() -> None:
    """z_scale should multiply x,y but not z."""
    from sciona.atoms.particle_tracking.detector_corrections.atoms import coordinate_rescaling_for_knn

    coords = np.array([[100.0, 0.0, 50.0]])
    r1 = coordinate_rescaling_for_knn(coords, cyl_mean_r2=100.0, z_scale=1.0)
    r5 = coordinate_rescaling_for_knn(coords, cyl_mean_r2=100.0, z_scale=5.0)

    assert np.allclose(r5[:, 0], r1[:, 0] * 5.0, rtol=1e-10)
    assert np.allclose(r5[:, 1], r1[:, 1] * 5.0, rtol=1e-10)
    assert np.allclose(r5[:, 2], r1[:, 2], rtol=1e-10)


def test_cap_correction_zero_displacement_no_change() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import perturbative_cap_correction

    n = 5
    xi = np.full(n, 100.0)
    yi = np.full(n, 50.0)
    hel_pitch = np.full(n, 500.0)
    charge_sign = np.ones(n)
    dp0_radial = np.zeros(n)
    dp1_azimuthal = np.zeros(n)

    xi_c, yi_c = perturbative_cap_correction(
        xi, yi, hel_pitch, charge_sign, dp0_radial, dp1_azimuthal,
    )
    assert np.allclose(xi_c, xi, atol=1e-15)
    assert np.allclose(yi_c, yi, atol=1e-15)


def test_cap_correction_opposite_charges_opposite_sign() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import perturbative_cap_correction

    n = 5
    xi = np.full(n, 100.0)
    yi = np.full(n, 50.0)
    hel_pitch = np.full(n, 500.0)
    dp0_radial = np.ones(n) * 5.0
    dp1_azimuthal = np.ones(n) * 3.0

    xi_pos, yi_pos = perturbative_cap_correction(
        xi, yi, hel_pitch, np.ones(n), dp0_radial, dp1_azimuthal,
    )
    xi_neg, yi_neg = perturbative_cap_correction(
        xi, yi, hel_pitch, -np.ones(n), dp0_radial, dp1_azimuthal,
    )

    dx_pos = xi_pos - xi
    dx_neg = xi_neg - xi
    assert np.allclose(dx_pos, -dx_neg), "Opposite charges should give opposite x corrections"


def test_cylinder_correction_zero_displacement_no_change() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import perturbative_cylinder_correction

    n = 5
    xi = np.full(n, 100.0)
    yi = np.full(n, 50.0)
    zi = np.full(n, 200.0)
    hel_r = np.full(n, 100.0)
    hel_pitch = np.full(n, 500.0)
    charge_sign = np.ones(n)

    xi_c, yi_c, zi_c = perturbative_cylinder_correction(
        xi, yi, zi, hel_r, hel_pitch, charge_sign, np.zeros(n), np.zeros(n),
    )
    assert np.allclose(xi_c, xi, atol=1e-15)
    assert np.allclose(yi_c, yi, atol=1e-15)
    assert np.allclose(zi_c, zi, atol=1e-15)


def test_cylinder_correction_has_dz_component() -> None:
    """Cylinder corrections should modify z when dp0_z is nonzero."""
    from sciona.atoms.particle_tracking.detector_corrections.atoms import perturbative_cylinder_correction

    n = 5
    xi = np.full(n, 100.0)
    yi = np.full(n, 50.0)
    zi = np.full(n, 200.0)
    hel_r = np.full(n, 100.0)
    hel_pitch = np.full(n, 500.0)
    charge_sign = np.ones(n)
    dp0_z = np.ones(n) * 10.0
    dp1_azimuthal = np.zeros(n)

    xi_c, yi_c, zi_c = perturbative_cylinder_correction(
        xi, yi, zi, hel_r, hel_pitch, charge_sign, dp0_z, dp1_azimuthal,
    )
    assert not np.allclose(zi_c, zi), "Expected nonzero dz for nonzero dp0_z"


def test_cylinder_correction_opposite_charges() -> None:
    from sciona.atoms.particle_tracking.detector_corrections.atoms import perturbative_cylinder_correction

    n = 5
    xi = np.full(n, 100.0)
    yi = np.full(n, 50.0)
    zi = np.full(n, 200.0)
    hel_r = np.full(n, 100.0)
    hel_pitch = np.full(n, 500.0)
    dp0_z = np.ones(n) * 5.0
    dp1_azimuthal = np.ones(n) * 3.0

    xi_p, yi_p, zi_p = perturbative_cylinder_correction(
        xi, yi, zi, hel_r, hel_pitch, np.ones(n), dp0_z, dp1_azimuthal,
    )
    xi_n, yi_n, zi_n = perturbative_cylinder_correction(
        xi, yi, zi, hel_r, hel_pitch, -np.ones(n), dp0_z, dp1_azimuthal,
    )

    assert np.allclose(xi_p - xi, -(xi_n - xi)), "Opposite charges, opposite dx"
    assert np.allclose(zi_p - zi, -(zi_n - zi)), "Opposite charges, opposite dz"


def test_detector_corrections_register_symbolic_metadata() -> None:
    import sciona.atoms.particle_tracking.detector_corrections.atoms  # noqa: F401

    rescaling = REGISTRY["coordinate_rescaling_for_knn"]["symbolic"]
    cap = REGISTRY["perturbative_cap_correction"]["symbolic"]
    cylinder = REGISTRY["perturbative_cylinder_correction"]["symbolic"]

    assert rescaling is not None
    assert rescaling.validity_bounds["cyl_mean_r2"] == (0.0, None)
    assert rescaling.check_dimensional_consistency() == []
    x, cyl_mean_r2, z_scale, r_xy = sp.symbols(
        "x cyl_mean_r2 z_scale r_xy"
    )
    assert str(rescaling.to_sympy().lhs) == "x_scaled"
    assert (
        sp.simplify(
            rescaling.to_sympy().rhs
            - (x * cyl_mean_r2 * z_scale / r_xy)
        )
        == 0
    )

    assert cap is not None
    assert cap.validity_bounds["hel_p_abs"] == (0.0, None)
    assert cap.check_dimensional_consistency() == []

    assert cylinder is not None
    assert cylinder.validity_bounds["hel_r"] == (0.0, None)
    assert cylinder.validity_bounds["curvature_radius"] == (0.0, None)
    assert cylinder.check_dimensional_consistency() == []
