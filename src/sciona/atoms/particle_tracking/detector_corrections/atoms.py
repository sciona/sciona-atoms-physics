"""Detector corrections for helix-surface intersections and kNN searches.

These atoms apply coordinate transformations and perturbative corrections
needed by the track matching pipeline: cylindrical coordinate rescaling
for k-nearest-neighbor searches, and per-intersection displacement
corrections for cap and cylinder detector surfaces.

The rescaling atom normalizes hit positions onto a reference cylinder
so that Euclidean k-NN distances are meaningful across detector layers.
The correction atoms apply learned displacement functions in local
polar coordinates, scaled by particle charge and helix geometry.

All functions are fully vectorized over arrays of shape (N,) or (N,3).

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
    witness_coordinate_rescaling_for_knn,
    witness_perturbative_cap_correction,
    witness_perturbative_cylinder_correction,
)


@register_atom(witness_coordinate_rescaling_for_knn)
@icontract.require(lambda coords: coords.ndim == 2 and coords.shape[1] == 3, "coords must be (N, 3)")
@icontract.require(lambda cyl_mean_r2: cyl_mean_r2 > 0, "cyl_mean_r2 must be positive")
@icontract.ensure(lambda result: np.all(np.isfinite(result)), "output must be finite")
def coordinate_rescaling_for_knn(
    coords: NDArray[np.float64],
    cyl_mean_r2: float = 1.0,
    z_scale: float = 1.0,
) -> NDArray[np.float64]:
    """Rescale 3D coordinates for k-NN neighbor searches in detector geometry.

    Projects hit positions onto a reference cylinder of radius cyl_mean_r2
    by scaling each point by (cyl_mean_r2 / actual_r), then applies z_scale
    to the x,y components. This normalization makes Euclidean k-NN distances
    meaningful across the detector's cylindrical layers.

    The rescaling is: x' = x * (cyl_mean_r2/r) * z_scale,
    y' = y * (cyl_mean_r2/r) * z_scale, z' = z * (cyl_mean_r2/r).

    Args:
        coords: Hit positions, shape (N, 3) with columns [x, y, z].
        cyl_mean_r2: Mean cylindrical radius to project onto.
        z_scale: Scale factor applied to x,y after projection.

    Returns:
        Rescaled coordinates, shape (N, 3).
    """
    vr2 = np.sqrt(np.square(coords[:, 0]) + np.square(coords[:, 1]))
    safe_vr2 = np.where(vr2 > 0, vr2, 1.0)
    scale = cyl_mean_r2 / safe_vr2

    vnorm = coords * scale[:, np.newaxis]
    vnorm[:, 0] *= z_scale
    vnorm[:, 1] *= z_scale

    return vnorm


@register_atom(witness_perturbative_cap_correction)
@icontract.require(lambda xi: len(xi) >= 1, "need at least one intersection point")
@icontract.ensure(lambda result: all(np.all(np.isfinite(a)) for a in result), "corrections must be finite")
def perturbative_cap_correction(
    xi: NDArray[np.float64],
    yi: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    charge_sign: NDArray[np.float64],
    dp0_radial: NDArray[np.float64],
    dp1_azimuthal: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Apply perturbative displacement correction at cap intersections.

    For cap (z-plane) intersections, the correction displaces in the
    radial and azimuthal directions in the x,y-plane, scaled by
    charge / |pitch/(2*pi)|.

    The radial unit vector at (xi, yi) is (xi/r, yi/r), and the
    azimuthal unit vector is (-yi/r, xi/r).

    Derived from HelixCorrector.correctCapIntersections in the TrackML
    5th-place solution (Steiner, 2018).

    Args:
        xi, yi: Uncorrected intersection x,y-coordinates, shape (N,).
        hel_pitch: Helix pitch, shape (N,).
        charge_sign: Particle charge sign (+1 or -1), shape (N,).
        dp0_radial: Radial displacement function value, shape (N,).
        dp1_azimuthal: Azimuthal displacement function value, shape (N,).

    Returns:
        (xi_corrected, yi_corrected): Corrected coordinates, each shape (N,).
    """
    r2 = np.sqrt(np.square(xi) + np.square(yi))
    safe_r2 = np.where(r2 > 0, r2, 1.0)

    ur2_x = xi / safe_r2
    ur2_y = yi / safe_r2
    uphi_x = -ur2_y
    uphi_y = ur2_x

    hel_p_abs = np.abs(hel_pitch / (2 * np.pi))
    safe_p = np.where(hel_p_abs > 0, hel_p_abs, 1.0)

    dx = (ur2_x * dp0_radial + uphi_x * dp1_azimuthal) * charge_sign / safe_p
    dy = (ur2_y * dp0_radial + uphi_y * dp1_azimuthal) * charge_sign / safe_p

    return xi + dx, yi + dy


@register_atom(witness_perturbative_cylinder_correction)
@icontract.require(lambda xi: len(xi) >= 1, "need at least one intersection point")
@icontract.require(lambda hel_r: np.all(hel_r > 0), "helix radii must be positive")
@icontract.ensure(lambda result: all(np.all(np.isfinite(a)) for a in result), "corrections must be finite")
def perturbative_cylinder_correction(
    xi: NDArray[np.float64],
    yi: NDArray[np.float64],
    zi: NDArray[np.float64],
    hel_r: NDArray[np.float64],
    hel_pitch: NDArray[np.float64],
    charge_sign: NDArray[np.float64],
    dp0_z: NDArray[np.float64],
    dp1_azimuthal: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Apply perturbative displacement correction at cylinder intersections.

    For cylinder intersections, the correction displaces in the
    azimuthal direction in x,y and in the z-direction. Both are scaled
    by charge / curvature_radius, where curvature_radius =
    (r^2 + p^2) / r (with p = pitch / 2*pi).

    Derived from HelixCorrector.correctCylinderIntersections in the
    TrackML 5th-place solution (Steiner, 2018).

    Args:
        xi, yi, zi: Uncorrected intersection coordinates, shape (N,).
        hel_r: Helix radius in x,y-plane, shape (N,).
        hel_pitch: Helix pitch, shape (N,).
        charge_sign: Particle charge sign (+1 or -1), shape (N,).
        dp0_z: Z-displacement function value, shape (N,).
        dp1_azimuthal: Azimuthal displacement function value, shape (N,).

    Returns:
        (xi_c, yi_c, zi_c): Corrected coordinates, each shape (N,).
    """
    r2 = np.sqrt(np.square(xi) + np.square(yi))
    safe_r2 = np.where(r2 > 0, r2, 1.0)

    uphi_x = -yi / safe_r2
    uphi_y = xi / safe_r2

    hel_p_abs = np.abs(hel_pitch / (2 * np.pi))
    hel_cr = (np.square(hel_r) + np.square(hel_p_abs)) / hel_r

    dx = uphi_x * dp1_azimuthal * charge_sign / hel_cr
    dy = uphi_y * dp1_azimuthal * charge_sign / hel_cr
    dz = dp0_z * charge_sign / hel_cr

    return xi + dx, yi + dy, zi + dz
