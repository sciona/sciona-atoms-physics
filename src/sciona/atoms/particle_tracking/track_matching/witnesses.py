"""Ghost witnesses for track matching primitives."""

from __future__ import annotations

from sciona.ghost.abstract import AbstractArray


def witness_helix_cylinder_intersection(
    x0: AbstractArray, y0: AbstractArray, z0: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    hel_r: AbstractArray, hel_pitch: AbstractArray,
    sign_uz: AbstractArray, target_r2sqr: AbstractArray,
) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for helix-cylinder intersection. Returns (xi, yi, zi, dphi)."""
    return (
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
    )


def witness_helix_cap_intersection(
    x0: AbstractArray, y0: AbstractArray, z0: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    hel_r: AbstractArray, hel_pitch: AbstractArray,
    target_z: AbstractArray,
) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for helix-cap intersection. Returns (xi, yi, zi, dphi)."""
    return (
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
        AbstractArray(shape=x0.shape, dtype="float64"),
    )


def witness_bayesian_neighbor_evaluation(
    d_theta: AbstractArray, d_phi: AbstractArray,
    bg_theta: AbstractArray, bg_phi: AbstractArray,
    e_theta: AbstractArray, e_phi: AbstractArray,
    cut_factor: float, dist_trust: float,
) -> tuple[AbstractArray, AbstractArray]:
    """Ghost witness for Bayesian neighbor evaluation. Returns (good, dubious)."""
    return (
        AbstractArray(shape=d_theta.shape, dtype="bool"),
        AbstractArray(shape=d_theta.shape, dtype="bool"),
    )


def witness_greedy_track_commit(
    hit_matrix: AbstractArray, used: AbstractArray,
    min_nhits: int, max_nloss: int,
    max_loss_fraction: float, max_nrows: int,
) -> tuple[AbstractArray, AbstractArray]:
    """Ghost witness for greedy track commit. Returns (hit_matrix, used)."""
    return (
        AbstractArray(shape=hit_matrix.shape, dtype="int64"),
        AbstractArray(shape=used.shape, dtype="bool"),
    )
