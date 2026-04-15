from __future__ import annotations

from sciona.ghost.abstract import AbstractArray, AbstractScalar


def witness_find_fof_clusters(
    x: AbstractArray,
    b: AbstractScalar,
    L: AbstractScalar,
    mode: AbstractScalar,
    max_neighbors: AbstractScalar | None,
    batch_size: AbstractScalar | None,
) -> AbstractArray:
    """Return integer label metadata for the jFOF cluster wrapper."""
    first_dim = x.shape[0] if x.shape else "N"
    return AbstractArray(shape=(first_dim,), dtype="int64")
