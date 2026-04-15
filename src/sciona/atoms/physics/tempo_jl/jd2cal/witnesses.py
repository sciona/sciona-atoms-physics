from __future__ import annotations
from sciona.ghost.abstract import AbstractArray, AbstractDistribution, AbstractScalar, AbstractSignal

def witness_date(offset: AbstractArray) -> AbstractArray:
    """Shape-and-type check for date. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=offset.shape,
        dtype="float64",
    )
    return result

def witness_date(year: AbstractArray, dayinyear: AbstractArray) -> AbstractArray:
    """Shape-and-type check for date. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=year.shape,
        dtype="float64",
    )
    return result

def witness_show(io: AbstractArray, d: AbstractArray) -> AbstractArray:
    """Shape-and-type check for show. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=io.shape,
        dtype="float64",
    )
    return result

def witness_time(hour: AbstractArray, minute: AbstractArray, second: AbstractArray) -> AbstractArray:
    """Shape-and-type check for time. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=hour.shape,
        dtype="float64",
    )
    return result

def witness_time(secondinday: AbstractArray, fraction: AbstractArray) -> AbstractArray:
    """Shape-and-type check for time. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=secondinday.shape,
        dtype="float64",
    )
    return result

def witness_time(secondinday: AbstractArray) -> AbstractArray:
    """Shape-and-type check for time. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=secondinday.shape,
        dtype="float64",
    )
    return result

def witness_show(io: AbstractArray, t: AbstractArray) -> AbstractArray:
    """Shape-and-type check for show. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=io.shape,
        dtype="float64",
    )
    return result

def witness_datetime(year: AbstractArray, month: AbstractArray, day: AbstractArray, hour: AbstractArray, min: AbstractArray, sec: AbstractArray) -> AbstractArray:
    """Shape-and-type check for datetime. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=year.shape,
        dtype="float64",
    )
    return result

def witness_datetime(s: AbstractArray) -> AbstractArray:
    """Shape-and-type check for datetime. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=s.shape,
        dtype="float64",
    )
    return result

def witness_datetime(seconds: AbstractArray) -> AbstractArray:
    """Shape-and-type check for datetime. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=seconds.shape,
        dtype="float64",
    )
    return result
