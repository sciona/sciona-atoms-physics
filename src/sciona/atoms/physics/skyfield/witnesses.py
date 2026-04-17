from __future__ import annotations

from sciona.ghost.abstract import AbstractArray, AbstractScalar


def witness_compute_spherical_coordinate_rates(
    r: AbstractArray,
    v: AbstractArray,
) -> tuple[
    AbstractScalar,
    AbstractScalar,
    AbstractScalar,
    AbstractScalar,
    AbstractScalar,
    AbstractScalar,
]:
    """Shape-and-type check for the Skyfield spherical-coordinate projection."""
    del r, v
    scalar = AbstractScalar(dtype="float64")
    return (scalar, scalar, scalar, scalar, scalar, scalar)


def witness_calculate_vector_angle(u: AbstractArray, v: AbstractArray) -> AbstractScalar:
    """Shape-and-type check for angle_between returning a scalar angle."""
    del u, v
    return AbstractScalar(dtype="float64")
