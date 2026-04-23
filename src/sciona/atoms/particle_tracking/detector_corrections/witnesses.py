"""Ghost witnesses for detector correction primitives."""

from __future__ import annotations

from sciona.ghost.abstract import AbstractArray


def witness_coordinate_rescaling_for_knn(
    coords: AbstractArray,
    cyl_mean_r2: float,
    z_scale: float,
) -> AbstractArray:
    """Ghost witness for coordinate rescaling. Returns rescaled (N,3) array."""
    return AbstractArray(shape=coords.shape, dtype="float64")


def witness_perturbative_cap_correction(
    xi: AbstractArray, yi: AbstractArray,
    hel_pitch: AbstractArray, charge_sign: AbstractArray,
    dp0_radial: AbstractArray, dp1_azimuthal: AbstractArray,
) -> tuple[AbstractArray, AbstractArray]:
    """Ghost witness for cap correction. Returns (xi_corrected, yi_corrected)."""
    return (
        AbstractArray(shape=xi.shape, dtype="float64"),
        AbstractArray(shape=xi.shape, dtype="float64"),
    )


def witness_perturbative_cylinder_correction(
    xi: AbstractArray, yi: AbstractArray, zi: AbstractArray,
    hel_r: AbstractArray, hel_pitch: AbstractArray,
    charge_sign: AbstractArray,
    dp0_z: AbstractArray, dp1_azimuthal: AbstractArray,
) -> tuple[AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for cylinder correction. Returns (xi_c, yi_c, zi_c)."""
    return (
        AbstractArray(shape=xi.shape, dtype="float64"),
        AbstractArray(shape=xi.shape, dtype="float64"),
        AbstractArray(shape=xi.shape, dtype="float64"),
    )
