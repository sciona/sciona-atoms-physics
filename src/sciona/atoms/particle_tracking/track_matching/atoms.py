"""Track matching primitives for charged particle track reconstruction.

These atoms implement the core operations for extending candidate tracks
through detector layers: helix-surface intersection (cylinder and cap
geometries), Bayesian neighbor evaluation for selecting the best
hit extension, and greedy track commitment with deduplication.

The intersection atoms extract the pure geometric computation from
the TrackML solution's CylinderIntersector/CapIntersector classes,
removing detector-specification coupling. The Bayesian evaluator
implements the signal-vs-background likelihood cut used to accept
or reject neighbor hits.

All functions except greedy_track_commit are fully vectorized over
arrays of shape (N,) representing batches of helices or candidate
tracks.

Derived from the 5th-place solution to the TrackML Particle Tracking
Challenge (Steiner, 2018).

Source: https://github.com/edwinst/trackml_solution (BSD 2-Clause)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

import icontract
from sciona.ghost.registry import register_atom

from .witnesses import (
    witness_helix_cylinder_intersection,
    witness_helix_cap_intersection,
    witness_bayesian_neighbor_evaluation,
    witness_greedy_track_commit,
)


@register_atom(witness_helix_cylinder_intersection)
@icontract.require(lambda x0: len(x0) >= 1, "need at least one helix")
@icontract.require(lambda hel_r: np.all(hel_r > 0), "helix radii must be positive")
@icontract.require(lambda target_r2sqr: np.all(target_r2sqr > 0), "target cylinder r^2 must be positive")
@icontract.ensure(lambda result: all(np.all(np.isfinite(a)) for a in result), "all outputs must be finite")
def helix_cylinder_intersection(
    x0: NDArray[np.float64],
    y0: NDArray[np.float64],
    z0: NDArray[np.float64],
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    hel_r: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    sign_uz: NDArray[np.float64],
    target_r2sqr: NDArray[np.float64],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Compute intersection of helical trajectories with a target cylinder.

    In r^2-space (r^2 = x^2 + y^2), a helix traces harmonic motion:
        r^2 = (rm^2 + r_h^2) + 2*rm*r_h * cos(phim0 + dphi)
    where rm = distance from origin to helix center and phim0 is the
    current phase relative to the max-r^2 point. The intersection with
    a cylinder at target_r2sqr is found by solving for dphi via arccos.

    From the four candidate dphi values (two crossings, forward and
    backward), the smallest positive value in the correct direction is
    selected.

    Args:
        x0, y0, z0: Starting point coordinates, each shape (N,).
        hel_xm, hel_ym: Helix center in x,y-plane, shape (N,).
        hel_r: Helix radius in x,y-plane, shape (N,).
        hel_pitch: Helix pitch (z-advance per 2*pi revolution), shape (N,).
        sign_uz: Sign of z-direction of motion (+1 or -1), shape (N,).
        target_r2sqr: Target cylinder radius squared, shape (N,).

    Returns:
        (xi, yi, zi, dphi): Intersection coordinates and phase advance,
        each shape (N,).
    """
    dx = x0 - hel_xm
    dy = y0 - hel_ym
    phi0 = np.arctan2(dy, dx)

    hel_rm = np.sqrt(np.square(hel_xm) + np.square(hel_ym))
    phim0 = phi0 - np.arctan2(hel_ym, hel_xm)
    phim0[phim0 < 0] += 2 * np.pi
    phim0[phim0 >= 2 * np.pi] -= 2 * np.pi

    hel_rm_sqr_plus_hel_r_sqr = np.square(hel_rm) + np.square(hel_r)
    two_hel_rm_hel_r = 2 * hel_rm * hel_r

    # Solve for the phase at which r^2 = target_r2sqr
    cos_val = (target_r2sqr - hel_rm_sqr_plus_hel_r_sqr) / two_hel_rm_hel_r
    cos_val = np.clip(cos_val, -1.0, 1.0)
    next_arccos = np.arccos(cos_val)

    sign_dphi = np.sign(sign_uz * hel_pitch)

    # Four candidate dphi values: two crossing phases, each +/- 2*pi
    cand_dphi = np.zeros((x0.shape[0], 4))
    cand_dphi[:, 0] = next_arccos - phim0
    cand_dphi[:, 1] = -next_arccos - phim0
    cand_dphi[:, 2] = cand_dphi[:, 0] + 2 * np.pi
    cand_dphi[:, 3] = cand_dphi[:, 1] + 2 * np.pi
    cand_dphi *= sign_dphi[:, np.newaxis]

    # Reject negative dphi (wrong direction); choose smallest positive
    dphi_tolerance = 1e-6
    cand_dphi[cand_dphi < dphi_tolerance] = np.inf
    dphi = sign_dphi * np.amin(cand_dphi, axis=1)

    # Clamp any remaining inf to 0 for finite output guarantee
    dphi[np.isinf(dphi)] = 0.0

    # Rotate helix to compute intersection point
    hel_p = hel_pitch / (2 * np.pi)
    cos_dphi = np.cos(dphi)
    sin_dphi = np.sin(dphi)
    xi = hel_xm + cos_dphi * dx - sin_dphi * dy
    yi = hel_ym + sin_dphi * dx + cos_dphi * dy
    zi = z0 + dphi * hel_p

    return xi, yi, zi, dphi


@register_atom(witness_helix_cap_intersection)
@icontract.require(lambda x0: len(x0) >= 1, "need at least one helix")
@icontract.require(lambda hel_pitch: np.all(hel_pitch != 0), "helix pitch must be nonzero")
@icontract.ensure(lambda result: all(np.all(np.isfinite(a)) for a in result), "all outputs must be finite")
def helix_cap_intersection(
    x0: NDArray[np.float64],
    y0: NDArray[np.float64],
    z0: NDArray[np.float64],
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    hel_r: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    target_z: NDArray[np.float64],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Compute intersection of helical trajectories with a target cap (z-plane).

    For a helix with known pitch, the phase advance to reach a target
    z-coordinate is simply dphi = (target_z - z0) / (pitch / 2*pi).
    The x,y intersection point is found by rotating the initial offset
    from the helix center by dphi.

    Args:
        x0, y0, z0: Starting point coordinates, each shape (N,).
        hel_xm, hel_ym: Helix center in x,y-plane, shape (N,).
        hel_r: Helix radius in x,y-plane, shape (N,).
        hel_pitch: Helix pitch (z-advance per 2*pi revolution), shape (N,).
        target_z: Target z-coordinate of the cap, shape (N,).

    Returns:
        (xi, yi, zi, dphi): Intersection coordinates and phase advance,
        each shape (N,).
    """
    hel_p = hel_pitch / (2 * np.pi)
    dphi = (target_z - z0) / hel_p

    dx = x0 - hel_xm
    dy = y0 - hel_ym
    cos_dphi = np.cos(dphi)
    sin_dphi = np.sin(dphi)
    xi = hel_xm + cos_dphi * dx - sin_dphi * dy
    yi = hel_ym + sin_dphi * dx + cos_dphi * dy
    zi = target_z.copy()

    return xi, yi, zi, dphi


@register_atom(witness_bayesian_neighbor_evaluation)
@icontract.require(lambda d_theta: len(d_theta) >= 1, "need at least one neighbor")
@icontract.require(lambda e_theta: np.all(e_theta > 0), "error estimates must be positive")
@icontract.require(lambda e_phi: np.all(e_phi > 0), "error estimates must be positive")
@icontract.require(lambda cut_factor: cut_factor > 0, "cut factor must be positive")
@icontract.require(lambda dist_trust: dist_trust > 0, "dist trust must be positive")
@icontract.ensure(lambda result: result[0].dtype == np.bool_ and result[1].dtype == np.bool_, "outputs must be boolean")
def bayesian_neighbor_evaluation(
    d_theta: NDArray[np.float64],
    d_phi: NDArray[np.float64],
    bg_theta: NDArray[np.float64],
    bg_phi: NDArray[np.float64],
    e_theta: NDArray[np.float64],
    e_phi: NDArray[np.float64],
    cut_factor: float = 3.0,
    dist_trust: float = 0.5,
) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """Evaluate neighbor hits using a Bayesian signal-vs-background cut.

    Computes the error-normalized displacement of each neighbor and
    compares it against a Bayesian threshold derived from the background
    hit density. The threshold increases logarithmically with the ratio
    of background distance to error estimate, implementing a likelihood
    ratio test.

    Args:
        d_theta, d_phi: Angular displacement to neighbor, shape (N,).
        bg_theta, bg_phi: Background hit mean distances, shape (N,).
        e_theta, e_phi: Estimated measurement errors, shape (N,).
        cut_factor: Multiplier for the Bayesian cut threshold.
        dist_trust: Fraction of the cut above which neighbors are dubious.

    Returns:
        (good, dubious): Boolean arrays, shape (N,).
            good[i] is True if neighbor i passes the Bayesian cut.
            dubious[i] is True if neighbor i is marginal (de > dist_trust * cut).
    """
    de_theta = d_theta / e_theta
    de_phi = d_phi / e_phi
    dbe_theta = bg_theta / e_theta
    dbe_phi = bg_phi / e_phi

    de = np.sqrt(np.square(de_theta) + np.square(de_phi))

    cut = cut_factor * np.sqrt(
        2 * np.log(
            (2 * np.square(dbe_theta) / np.pi + 1)
            * (2 * np.square(dbe_phi) / np.pi + 1)
        )
    )

    good = de < cut
    dubious = de > dist_trust * cut

    return good, dubious


@register_atom(witness_greedy_track_commit)
@icontract.require(lambda hit_matrix: hit_matrix.ndim == 2, "hit_matrix must be 2D")
@icontract.require(lambda used: used.ndim == 1, "used must be 1D")
@icontract.require(lambda min_nhits: min_nhits >= 1, "min_nhits must be at least 1")
@icontract.ensure(lambda result: result[0].ndim == 2 and result[1].ndim == 1, "output shapes must match input")
def greedy_track_commit(
    hit_matrix: NDArray[np.int64],
    used: NDArray[np.bool_],
    min_nhits: int = 3,
    max_nloss: int = 100,
    max_loss_fraction: float = 1.0,
    max_nrows: int = 100000,
) -> tuple[NDArray[np.int64], NDArray[np.bool_]]:
    """Commit candidate tracks greedily, deduplicating shared hits.

    Iterates over rows of the hit matrix top-to-bottom. For each row,
    hits already marked as used (from prior rows or the input used array)
    are zeroed out. Rows that fail the minimum-hits or maximum-loss
    criteria are discarded entirely.

    This operation is inherently sequential: each row's decision depends
    on which hits were claimed by all preceding rows.

    Args:
        hit_matrix: Integer array of shape (N, M) containing hit IDs.
            Zeros represent empty slots.
        used: Boolean array of shape (max_hit_id + 1,). used[i] is True
            if hit ID i has already been claimed.
        min_nhits: Minimum number of first-occurrence hits for a row
            to be accepted.
        max_nloss: Maximum number of already-used hits allowed per row.
        max_loss_fraction: Maximum fraction of already-used hits per row.
        max_nrows: Maximum number of rows to accept.

    Returns:
        (hit_matrix, used): Modified copies. Discarded rows are zeroed;
        used is updated to reflect all committed hits.
    """
    hit_matrix = hit_matrix.copy()
    used = used.copy()
    used[0] = True  # hit_id 0 is the empty-slot sentinel

    nrows_taken = 0
    for i_row in range(hit_matrix.shape[0]):
        row = hit_matrix[i_row, :]
        nhits = np.sum(row != 0)
        if nhits == 0:
            hit_matrix[i_row, :] = 0
            continue
        mask_first = ~used[row]
        nfirst = np.sum(mask_first)
        nloss = nhits - nfirst
        loss_fraction = nloss / nhits
        if (nfirst < min_nhits
                or nloss > max_nloss
                or loss_fraction > max_loss_fraction
                or nrows_taken >= max_nrows):
            hit_matrix[i_row, :] = 0
        else:
            used[row] = True
            hit_matrix[i_row, :] *= mask_first
            nrows_taken += 1

    return hit_matrix, used
