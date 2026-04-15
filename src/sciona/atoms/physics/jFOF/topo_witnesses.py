from __future__ import annotations

from sciona.ghost.abstract import AbstractArray, AbstractScalar


def witness_topological_loss_computation(
    key: AbstractArray,
    logits: AbstractArray,
    pos32: AbstractArray,
    nbr_idx: AbstractArray,
    b: AbstractArray,
    max_iters: AbstractArray,
    tau: AbstractArray,
) -> AbstractArray:
    """Shape-and-type check for topological loss computation."""
    return AbstractArray(shape=key.shape, dtype="float64")


def witness_compute_topo_loss(
    key: AbstractArray,
    logits: AbstractArray,
    pos32: AbstractArray,
    nbr_idx: AbstractArray,
    b: AbstractArray,
    max_iters: AbstractScalar,
    tau: AbstractScalar,
) -> AbstractScalar:
    """Shape-and-type check for compute topo loss."""
    return AbstractScalar(dtype="float64")
