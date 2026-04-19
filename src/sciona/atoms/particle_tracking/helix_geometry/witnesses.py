"""Ghost witnesses for helix geometry primitives."""

from __future__ import annotations

from sciona.ghost.abstract import AbstractArray


def witness_circle_from_three_points(
    x1: AbstractArray, y1: AbstractArray,
    x2: AbstractArray, y2: AbstractArray,
    x3: AbstractArray, y3: AbstractArray,
    large_radius: float = 1e6,
) -> tuple[AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for circle fitting. Same-shape input/output."""
    return (
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
    )


def witness_helix_pitch_from_two_points(
    x1: AbstractArray, y1: AbstractArray, z1: AbstractArray,
    x2: AbstractArray, y2: AbstractArray, z2: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    zero_pitch: float = 0.001,
) -> tuple[AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for two-point pitch. Returns (pitch, phid, dz)."""
    return (
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
    )


def witness_helix_pitch_least_squares(
    x1: AbstractArray, y1: AbstractArray, z1: AbstractArray,
    x2: AbstractArray, y2: AbstractArray, z2: AbstractArray,
    x3: AbstractArray, y3: AbstractArray, z3: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    zero_pitch: float = 0.001,
) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for three-point pitch. Returns (pitch, phid, dz, loss)."""
    return (
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
        AbstractArray(shape=x1.shape, dtype="float64"),
    )


def witness_helix_direction_from_two_points(
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    hel_pitch: AbstractArray,
    x1: AbstractArray, y1: AbstractArray, z1: AbstractArray,
    x2: AbstractArray, y2: AbstractArray, z2: AbstractArray,
) -> AbstractArray:
    """Ghost witness for direction. Returns scalar direction per helix."""
    return AbstractArray(shape=hel_xm.shape, dtype="float64")


def witness_helix_nearest_point_distance(
    x0: AbstractArray, y0: AbstractArray, z0: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray,
    hel_r: AbstractArray, hel_pitch: AbstractArray,
    x: AbstractArray, y: AbstractArray, z: AbstractArray,
    iterations: int = 3,
) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    """Ghost witness for nearest-point. Returns (x1, y1, z1, dist)."""
    return (
        AbstractArray(shape=x.shape, dtype="float64"),
        AbstractArray(shape=x.shape, dtype="float64"),
        AbstractArray(shape=x.shape, dtype="float64"),
        AbstractArray(shape=x.shape, dtype="float64"),
    )
