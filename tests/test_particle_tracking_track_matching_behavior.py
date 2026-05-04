from __future__ import annotations

import numpy as np
import sympy as sp

from sciona.ghost.registry import REGISTRY


def test_all_four_atoms_import() -> None:
    from sciona.atoms.particle_tracking.track_matching.atoms import (
        helix_cylinder_intersection,
        helix_cap_intersection,
        bayesian_neighbor_evaluation,
        greedy_track_commit,
    )
    assert callable(helix_cylinder_intersection)
    assert callable(helix_cap_intersection)
    assert callable(bayesian_neighbor_evaluation)
    assert callable(greedy_track_commit)


def test_helix_cylinder_intersection_output_on_cylinder() -> None:
    """Output points must satisfy xi^2 + yi^2 approx target_r2sqr."""
    from sciona.atoms.particle_tracking.track_matching.atoms import helix_cylinder_intersection

    n = 8
    # Helix centered at (3, 0) with radius 2 -> sweeps r^2 from 1 to 25
    x0 = np.full(n, 5.0)  # start at (5, 0): on outer edge
    y0 = np.zeros(n)
    z0 = np.zeros(n)
    hel_xm = np.full(n, 3.0)
    hel_ym = np.zeros(n)
    hel_r = np.full(n, 2.0)
    hel_pitch = np.full(n, 10.0)
    sign_uz = np.ones(n)
    target_r2sqr = np.full(n, 9.0)  # r = 3

    xi, yi, zi, dphi = helix_cylinder_intersection(
        x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, sign_uz, target_r2sqr,
    )

    ri_sqr = np.square(xi) + np.square(yi)
    assert xi.shape == (n,)
    assert yi.shape == (n,)
    assert zi.shape == (n,)
    assert dphi.shape == (n,)
    assert np.allclose(ri_sqr, target_r2sqr, atol=0.5), (
        f"Intersection r^2={ri_sqr} should be near target {target_r2sqr}"
    )


def test_helix_cylinder_intersection_finite_outputs() -> None:
    from sciona.atoms.particle_tracking.track_matching.atoms import helix_cylinder_intersection

    n = 5
    x0 = np.full(n, 100.0)
    y0 = np.zeros(n)
    z0 = np.zeros(n)
    hel_xm = np.full(n, 50.0)
    hel_ym = np.zeros(n)
    hel_r = np.full(n, 50.0)
    hel_pitch = np.full(n, 500.0)
    sign_uz = np.ones(n)
    target_r2sqr = np.full(n, 5000.0)

    xi, yi, zi, dphi = helix_cylinder_intersection(
        x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, sign_uz, target_r2sqr,
    )
    assert np.all(np.isfinite(xi))
    assert np.all(np.isfinite(yi))
    assert np.all(np.isfinite(zi))
    assert np.all(np.isfinite(dphi))


def test_helix_cap_intersection_reaches_target_z() -> None:
    """Output zi must equal target_z."""
    from sciona.atoms.particle_tracking.track_matching.atoms import helix_cap_intersection

    n = 6
    x0 = np.full(n, 100.0)
    y0 = np.zeros(n)
    z0 = np.zeros(n)
    hel_xm = np.zeros(n)
    hel_ym = np.zeros(n)
    hel_r = np.full(n, 100.0)
    hel_pitch = np.full(n, 500.0)
    target_z = np.full(n, 200.0)

    xi, yi, zi, dphi = helix_cap_intersection(
        x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, target_z,
    )

    assert xi.shape == (n,)
    assert np.allclose(zi, 200.0, atol=1e-10), f"Expected zi=200, got {zi}"
    # xi^2 + yi^2 should equal hel_r^2 (helix stays on circle of radius hel_r around center)
    ri_sqr = np.square(xi - hel_xm) + np.square(yi - hel_ym)
    assert np.allclose(ri_sqr, np.square(hel_r), atol=1e-6)


def test_helix_cap_intersection_negative_z() -> None:
    from sciona.atoms.particle_tracking.track_matching.atoms import helix_cap_intersection

    n = 5
    x0 = np.full(n, 50.0)
    y0 = np.zeros(n)
    z0 = np.full(n, 100.0)
    hel_xm = np.zeros(n)
    hel_ym = np.zeros(n)
    hel_r = np.full(n, 50.0)
    hel_pitch = np.full(n, -200.0)
    target_z = np.full(n, -50.0)

    xi, yi, zi, dphi = helix_cap_intersection(
        x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, target_z,
    )
    assert np.allclose(zi, -50.0, atol=1e-10)


def test_bayesian_neighbor_zero_distance_is_good() -> None:
    """A neighbor at distance 0 should always be flagged as good."""
    from sciona.atoms.particle_tracking.track_matching.atoms import bayesian_neighbor_evaluation

    n = 10
    d_theta = np.zeros(n)
    d_phi = np.zeros(n)
    bg_theta = np.ones(n) * 5.0
    bg_phi = np.ones(n) * 5.0
    e_theta = np.ones(n) * 0.1
    e_phi = np.ones(n) * 0.1

    good, dubious = bayesian_neighbor_evaluation(
        d_theta, d_phi, bg_theta, bg_phi, e_theta, e_phi,
        cut_factor=3.0, dist_trust=0.5,
    )

    assert good.dtype == np.bool_
    assert dubious.dtype == np.bool_
    assert np.all(good), "Zero-distance neighbors should all be good"
    assert not np.any(dubious), "Zero-distance neighbors should not be dubious"


def test_bayesian_neighbor_large_distance_is_bad() -> None:
    from sciona.atoms.particle_tracking.track_matching.atoms import bayesian_neighbor_evaluation

    n = 5
    d_theta = np.ones(n) * 100.0
    d_phi = np.ones(n) * 100.0
    bg_theta = np.ones(n) * 0.5
    bg_phi = np.ones(n) * 0.5
    e_theta = np.ones(n) * 0.1
    e_phi = np.ones(n) * 0.1

    good, dubious = bayesian_neighbor_evaluation(
        d_theta, d_phi, bg_theta, bg_phi, e_theta, e_phi,
        cut_factor=3.0, dist_trust=0.5,
    )

    assert not np.any(good), "Far neighbors should not be good"
    assert np.all(dubious), "Far neighbors should be dubious"


def test_greedy_track_commit_unique_rows_kept() -> None:
    """A matrix with fully unique rows should keep all of them."""
    from sciona.atoms.particle_tracking.track_matching.atoms import greedy_track_commit

    hit_matrix = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
    ], dtype=np.int64)
    used = np.zeros(13, dtype=bool)

    result_matrix, result_used = greedy_track_commit(
        hit_matrix, used, min_nhits=3,
    )

    assert np.all(result_used[1:13])
    assert np.array_equal(result_matrix, hit_matrix)


def test_greedy_track_commit_overlap_zeros_used() -> None:
    """Overlapping rows should have their used hits zeroed out."""
    from sciona.atoms.particle_tracking.track_matching.atoms import greedy_track_commit

    hit_matrix = np.array([
        [1, 2, 3],
        [2, 3, 4],  # hits 2,3 overlap with row 0
    ], dtype=np.int64)
    used = np.zeros(5, dtype=bool)

    result_matrix, result_used = greedy_track_commit(
        hit_matrix, used, min_nhits=3,
    )

    # Row 0 committed (3 unique hits). Row 1 has only 1 unique hit < min_nhits.
    assert np.all(result_matrix[1] == 0), f"Expected row 1 zeroed, got {result_matrix[1]}"


def test_greedy_track_commit_respects_max_nrows() -> None:
    from sciona.atoms.particle_tracking.track_matching.atoms import greedy_track_commit

    hit_matrix = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ], dtype=np.int64)
    used = np.zeros(10, dtype=bool)

    result_matrix, result_used = greedy_track_commit(
        hit_matrix, used, min_nhits=3, max_nrows=2,
    )

    # Only first 2 rows should be committed; row 3 zeroed
    assert np.all(result_matrix[2] == 0)
    assert not result_used[7] and not result_used[8] and not result_used[9]


def test_track_matching_atoms_register_symbolic_metadata() -> None:
    import sciona.atoms.particle_tracking.track_matching.atoms  # noqa: F401

    cylinder = REGISTRY["helix_cylinder_intersection"]["symbolic"]
    cap = REGISTRY["helix_cap_intersection"]["symbolic"]
    bayes = REGISTRY["bayesian_neighbor_evaluation"]["symbolic"]
    greedy = REGISTRY["greedy_track_commit"]["symbolic"]

    assert cylinder is not None
    assert cylinder.validity_bounds["target_r2sqr"] == (0.0, None)
    assert cylinder.check_dimensional_consistency() == []
    xi, yi = sp.symbols("xi yi")
    assert str(cylinder.to_sympy().lhs) == "target_r2sqr"
    assert sp.simplify(cylinder.to_sympy().rhs - (xi**2 + yi**2)) == 0

    assert cap is not None
    assert cap.validity_bounds["hel_p"] == (0.0, None)
    assert cap.check_dimensional_consistency() == []
    target_z, z0, hel_p = sp.symbols("target_z z0 hel_p")
    assert str(cap.to_sympy().lhs) == "dphi"
    assert sp.simplify(cap.to_sympy().rhs - ((target_z - z0) / hel_p)) == 0

    assert bayes is not None
    assert bayes.validity_bounds["e_theta"] == (0.0, None)
    assert bayes.check_dimensional_consistency() == []

    assert greedy is not None
    assert greedy.validity_bounds["loss_fraction"] == (0.0, 1.0)
    assert greedy.check_dimensional_consistency() == []
