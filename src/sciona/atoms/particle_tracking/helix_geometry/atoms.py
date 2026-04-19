"""Helix geometry primitives for charged particle track reconstruction.

In a uniform magnetic field along the z-axis, charged particles follow
helical trajectories. The x,y-projection is a circle whose radius encodes
the transverse momentum, and the pitch encodes the longitudinal momentum.

These atoms implement the core geometric operations for fitting and
querying helices from detector hit positions: circle fitting, pitch
estimation, direction determination, and nearest-point computation via
a Kepler-equation reduction.

All functions are fully vectorized — they operate on arrays of shape (N,)
representing batches of helices or points, enabling efficient processing
of ~100k hits per detector event.

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
    witness_circle_from_three_points,
    witness_helix_direction_from_two_points,
    witness_helix_nearest_point_distance,
    witness_helix_pitch_from_two_points,
    witness_helix_pitch_least_squares,
)


@register_atom(witness_circle_from_three_points)
@icontract.require(lambda x1: len(x1) >= 1, "need at least one point triple")
@icontract.ensure(lambda result: all(np.all(np.isfinite(a)) for a in result), "all outputs must be finite")
def circle_from_three_points(
    x1: NDArray[np.float64],
    y1: NDArray[np.float64],
    x2: NDArray[np.float64],
    y2: NDArray[np.float64],
    x3: NDArray[np.float64],
    y3: NDArray[np.float64],
    large_radius: float = 1e6,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Fit circles through triples of points in the x,y-plane.

    The x,y-projection of a charged particle helix in a uniform B-field is
    a circle, so fitting 3 detector hits in x,y gives the circle center and
    radius (which encodes the transverse momentum).

    Handles degenerate cases: collinear points get a large tangent circle,
    coincident points get a large circle through the origin. This is critical
    because with ~100k hits per event, degenerate triples inevitably occur.

    Args:
        x1, y1, x2, y2, x3, y3: Coordinates of the three points, each shape (N,).
        large_radius: Radius to use for degenerate (collinear/coincident) cases.

    Returns:
        (xm, ym, r): Circle center coordinates and radii, each shape (N,).
    """
    x21 = x2 - x1
    y21 = y2 - y1
    x31 = x3 - x1
    y31 = y3 - y1

    same21 = ~np.logical_or(x21.astype(bool), y21.astype(bool))
    same31 = ~np.logical_or(x31.astype(bool), y31.astype(bool))
    allsame = same21 & same31

    xd = np.where(allsame, x1, np.where(same21, x31, x21))
    yd = np.where(allsame, y1, np.where(same21, y31, y21))

    rsqr1 = np.square(x1) + np.square(y1)
    rsqr2 = np.square(x2) + np.square(y2)
    rsqr3 = np.square(x3) + np.square(y3)

    x32 = x3 - x2
    y32 = y3 - y2
    denom = 2.0 * (y1 * x32 - x1 * y32 + x2 * y3 - x3 * y2)
    r_too_large = denom == 0
    denom[r_too_large] = 1.0  # dummy to avoid division by zero

    xm = -(rsqr1 * y32 - rsqr2 * y31 + rsqr3 * y21) / denom
    ym = (rsqr1 * x32 - rsqr2 * x31 + rsqr3 * x21) / denom
    r = np.sqrt(np.square(x1 - xm) + np.square(y1 - ym))

    r_too_large |= r > large_radius
    r[r_too_large] = large_radius
    d_mag = np.sqrt(np.square(xd[r_too_large]) + np.square(yd[r_too_large]))
    d_mag[d_mag == 0] = 1.0  # avoid division by zero for allsame at origin
    r_over_d = large_radius / d_mag
    xm[r_too_large] = x1[r_too_large] - r_over_d * yd[r_too_large]
    ym[r_too_large] = y1[r_too_large] + r_over_d * xd[r_too_large]

    return xm, ym, r


@register_atom(witness_helix_pitch_from_two_points)
@icontract.require(lambda x1: len(x1) >= 1, "need at least one point pair")
@icontract.ensure(lambda result: np.all(np.isfinite(result[0])), "pitch must be finite")
def helix_pitch_from_two_points(
    x1: NDArray[np.float64],
    y1: NDArray[np.float64],
    z1: NDArray[np.float64],
    x2: NDArray[np.float64],
    y2: NDArray[np.float64],
    z2: NDArray[np.float64],
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    zero_pitch: float = 0.001,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Compute helix pitch from two points when the circle center is known.

    The points are assumed to be separated by less than half a turn. The
    pitch is the z-advance per full 2*pi revolution.

    Args:
        x1, y1, z1, x2, y2, z2: Coordinates of the two points, each shape (N,).
        hel_xm, hel_ym: Helix center coordinates in x,y-plane, shape (N,).
        zero_pitch: Replacement value for exactly-zero pitch to avoid singularity.

    Returns:
        (hel_pitch, phid, dz): Pitch, phase difference, and z-difference,
        each shape (N,).
    """
    phi1 = np.arctan2(y1 - hel_ym, x1 - hel_xm)
    phi2 = np.arctan2(y2 - hel_ym, x2 - hel_xm)
    phid = phi2 - phi1
    phid[phid > np.pi] -= 2 * np.pi
    phid[phid <= -np.pi] += 2 * np.pi

    dz = z2 - z1
    phid[phid == 0] = 0.001
    hel_pitch = dz / phid * 2 * np.pi

    has_zero_pitch = hel_pitch == 0.0
    hel_pitch[has_zero_pitch] = zero_pitch
    dz[has_zero_pitch] = zero_pitch * phid[has_zero_pitch] / (2 * np.pi)

    return hel_pitch, phid, dz


@register_atom(witness_helix_pitch_least_squares)
@icontract.require(lambda x1: len(x1) >= 1, "need at least one point triple")
@icontract.ensure(lambda result: np.all(np.isfinite(result[0])), "pitch must be finite")
def helix_pitch_least_squares(
    x1: NDArray[np.float64],
    y1: NDArray[np.float64],
    z1: NDArray[np.float64],
    x2: NDArray[np.float64],
    y2: NDArray[np.float64],
    z2: NDArray[np.float64],
    x3: NDArray[np.float64],
    y3: NDArray[np.float64],
    z3: NDArray[np.float64],
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    zero_pitch: float = 0.001,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Compute optimal helix pitch from three points via least-squares.

    Given the circle center (from circle_from_three_points), the
    z-coordinate is linear in the phase angle phi. This function
    performs linear regression of z vs phi for three points, including
    the sum-of-squared residuals as a track quality signal.

    Careful phase-unwrapping prevents 2*pi ambiguity errors.

    Args:
        x1..z3: Coordinates of three points in helix-path order, each shape (N,).
        hel_xm, hel_ym: Helix center coordinates, shape (N,).
        zero_pitch: Replacement value for zero pitch.

    Returns:
        (hel_pitch, phid, dz, loss): Pitch, phase difference (pt2 to pt3),
        z-difference (pt2 to pt3), and sum of squared residuals.
        Each shape (N,).
    """
    phi1 = np.arctan2(y1 - hel_ym, x1 - hel_xm)
    phi2 = np.arctan2(y2 - hel_ym, x2 - hel_xm)
    phi3 = np.arctan2(y3 - hel_ym, x3 - hel_xm)
    phid21 = phi2 - phi1
    phid31 = phi3 - phi1

    phid21[phid21 >= np.pi] -= 2 * np.pi
    phid21[phid21 < -np.pi] += 2 * np.pi

    phid21neg = phid21 < 0
    phid31[~phid21neg & (phid31 < phid21)] += 2 * np.pi
    phid31[phid21neg & (phid31 > phid21)] -= 2 * np.pi

    sum_phi = phid21 + phid31
    sum_phisqr = np.square(phid21) + np.square(phid31)
    sum_z = z1 + z2 + z3
    sum_zphi = z2 * phid21 + z3 * phid31
    n = 3.0
    denom = n * sum_phisqr - np.square(sum_phi)
    denom[denom == 0] = 1e-12  # avoid division by zero
    hel_p = (n * sum_zphi - sum_z * sum_phi) / denom
    hel_pitch = 2 * np.pi * hel_p
    dz = z3 - z2

    has_zero_pitch = hel_pitch == 0.0
    phid = phid31 - phid21
    hel_pitch[has_zero_pitch] = zero_pitch
    dz[has_zero_pitch] = zero_pitch * phid[has_zero_pitch] / (2 * np.pi)

    zs = np.stack([z1, z2, z3], axis=1)
    phis = np.stack([np.zeros_like(phid21), phid21, phid31], axis=1)
    zs -= (sum_z / n)[:, np.newaxis]
    phis -= (sum_phi / n)[:, np.newaxis]
    loss = np.sum(np.square(zs - hel_p[:, np.newaxis] * phis), axis=1)

    return hel_pitch, phid, dz, loss


@register_atom(witness_helix_direction_from_two_points)
@icontract.require(lambda hel_xm: len(hel_xm) >= 1, "need at least one helix")
@icontract.ensure(lambda result: np.all(np.isfinite(result)), "direction must be finite")
def helix_direction_from_two_points(
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    x1: NDArray[np.float64],
    y1: NDArray[np.float64],
    z1: NDArray[np.float64],
    x2: NDArray[np.float64],
    y2: NDArray[np.float64],
    z2: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Determine the z-direction of helix motion between two points.

    Returns a value whose sign specifies the sign of motion in z. Usually
    this is simply z2 - z1, but when the two points have the same
    z-coordinate, the function infers direction from the sense of rotation
    in the x,y-plane using the helix center and pitch.

    Args:
        hel_xm, hel_ym: Helix center coordinates, shape (N,).
        hel_pitch: Helix pitch values, shape (N,).
        x1, y1, z1, x2, y2, z2: Coordinates of two points, each shape (N,).

    Returns:
        hel_dz: Direction indicator, shape (N,). Sign gives z-direction.
    """
    hel_dz = z2 - z1
    nodz = hel_dz == 0
    hel_dz[nodz] = hel_pitch[nodz] * np.sign(
        (y1[nodz] - y2[nodz]) * (hel_xm[nodz] - x1[nodz])
        + (x2[nodz] - x1[nodz]) * (hel_ym[nodz] - y1[nodz])
    )
    return hel_dz


@register_atom(witness_helix_nearest_point_distance)
@icontract.require(lambda x: len(x) >= 1, "need at least one reference point")
@icontract.ensure(lambda result: np.all(result[3] >= 0), "distances must be non-negative")
def helix_nearest_point_distance(
    x0: NDArray[np.float64],
    y0: NDArray[np.float64],
    z0: NDArray[np.float64],
    hel_xm: NDArray[np.float64],
    hel_ym: NDArray[np.float64],
    hel_r: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    z: NDArray[np.float64],
    iterations: int = 3,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Find the nearest point on each helix to a reference point.

    Finding the nearest point on a 3D helix has no closed-form solution.
    This function recognizes the problem is equivalent to Kepler's equation
    E - e*sin(E) = M, where e is a ratio of helix radius times reference
    distance to squared pitch. It applies Newton's method (default 3
    iterations) to solve this transcendental equation.

    This connection to orbital mechanics is the key insight — it avoids
    iterative root-finding over the full parametric helix.

    Args:
        x0, y0, z0: Initial vertex on each helix, shape (N,) or scalar.
        hel_xm, hel_ym: Helix center coordinates, shape (N,) or scalar.
        hel_r: Helix radii in x,y-plane, shape (N,) or scalar.
        hel_pitch: Helix pitch values, shape (N,) or scalar.
        x, y, z: Reference point coordinates, shape (N,).
        iterations: Number of Newton's method iterations (default 3).

    Returns:
        (x1, y1, z1, dist): Nearest point coordinates and Euclidean
        distance, each shape (N,).
    """
    dx = x - hel_xm
    dy = y - hel_ym
    dx0 = x0 - hel_xm
    dy0 = y0 - hel_ym

    dr2 = np.sqrt(np.square(dx) + np.square(dy))
    hel_p = hel_pitch / (2 * np.pi)

    dph_z = (z - z0) / hel_p
    dph_xy = np.arctan2(dy, dx) - np.arctan2(dy0, dx0)
    dph_diff = dph_z - dph_xy

    e = hel_r * dr2 / np.square(hel_p)

    E = np.full(x.shape[0], np.pi)
    k = np.ceil(dph_diff / (2 * np.pi) - 0.5)
    M = np.pi + dph_diff - 2 * k * np.pi

    for _i in range(iterations):
        f = E - e * np.sin(E) - M
        fprime = 1.0 - e * np.cos(E)
        E = E - f / fprime

    u = E - np.pi + 2 * k * np.pi
    w = u - dph_diff
    z1 = z + hel_p * w

    dphi = (z - z0) / hel_p + w
    cos1 = np.cos(dphi)
    sin1 = np.sin(dphi)
    x1 = hel_xm + cos1 * dx0 - sin1 * dy0
    y1 = hel_ym + sin1 * dx0 + cos1 * dy0
    dist = np.sqrt(np.square(x - x1) + np.square(y - y1) + np.square(z - z1))

    return x1, y1, z1, dist
