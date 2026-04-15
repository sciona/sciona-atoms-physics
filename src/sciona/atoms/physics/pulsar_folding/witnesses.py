from __future__ import annotations
from sciona.ghost.abstract import AbstractArray, AbstractScalar, AbstractDistribution, AbstractSignal


def witness_dm_can_brute_force(data: AbstractArray) -> AbstractArray:
    """Shape-and-type check for dm can brute force. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=data.shape,
        dtype="float64",
    )
    return result


def witness_spline_bandpass_correction(data: AbstractArray) -> AbstractArray:
    """Shape-and-type check for spline bandpass correction. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=data.shape,
        dtype="float64",
    )
    return result
