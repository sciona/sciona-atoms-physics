from __future__ import annotations

from sciona.ghost.abstract import AbstractArray, AbstractDistribution, AbstractScalar, AbstractSignal


def witness_graph_time_scale_management(data: AbstractArray) -> AbstractArray:
    """Shape-and-type check for high precision duration. Returns output metadata without running the real computation."""
    return AbstractArray(shape=data.shape, dtype=data.dtype)


def witness_high_precision_duration(duration: AbstractScalar) -> AbstractArray:
    """Describe the scalar duration container used for high-precision timing."""
    return AbstractArray(shape=(), dtype=duration.dtype)
