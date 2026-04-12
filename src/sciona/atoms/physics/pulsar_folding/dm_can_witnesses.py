from __future__ import annotations

from ageoa.ghost.abstract import AbstractArray, AbstractScalar, AbstractDistribution, AbstractSignal


def witness_dm_candidate_filter(data: AbstractArray, data_base: AbstractArray, sens: AbstractArray, DM_base: AbstractArray, candidates: AbstractArray, fchan: AbstractArray, width: AbstractArray, tsamp: AbstractArray) -> AbstractArray:
    """Shape-and-type check for dm candidate filter. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=data.shape,
        dtype="float64",
    )
    return result
