from __future__ import annotations
from ageoa.ghost.abstract import AbstractArray, AbstractDistribution, AbstractScalar, AbstractSignal


def witness_show(io: AbstractScalar, s: AbstractScalar) -> AbstractScalar:
    """Shape-and-type check for show. Returns output metadata without running the real computation."""
    result = AbstractScalar(
        dtype="str",
    )
    return result


def witness__zero_offset(seconds: AbstractScalar) -> AbstractScalar:
    """Shape-and-type check for zero offset. Returns output metadata without running the real computation."""
    result = AbstractScalar(
        dtype="float64",
    )
    return result


def witness_apply_offsets(sec: AbstractScalar, ts1: AbstractScalar, ts2: AbstractScalar) -> AbstractScalar:
    """Shape-and-type check for apply offsets. Returns output metadata without running the real computation."""
    result = AbstractScalar(
        dtype="float64",
    )
    return result
