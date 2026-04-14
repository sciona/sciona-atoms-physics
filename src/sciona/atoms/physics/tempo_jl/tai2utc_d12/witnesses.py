from __future__ import annotations

from sciona.ghost.abstract import ANYTHING, AbstractArray, AbstractDistribution, AbstractScalar, AbstractSignal


def witness_utc_to_tai_leap_second_kernel(
    utc1: AbstractArray,
    utc2: AbstractArray,
) -> AbstractScalar:
    """
    to chase a symbolic back-edge into tai_to_utc_inversion when widening
    the return type, which was the root cause of the detected cycle.
    """
    _ = (utc1, utc2)
    result = AbstractScalar(
        dtype="float64",
        shape=(),
        ndim=0,
        values=ANYTHING,  # concrete sentinel - severs symbolic link to inversion path
    )
    return result

def witness_tai_to_utc_inversion(
    tai1: AbstractArray,
    tai2: AbstractArray,
    tai_estimate: AbstractArray,
) -> AbstractScalar:
    """Shape-and-type check for tai to utc inversion. Returns output metadata without running the real computation."""
    return AbstractScalar(dtype="float64", shape=(), ndim=0, values=ANYTHING)
