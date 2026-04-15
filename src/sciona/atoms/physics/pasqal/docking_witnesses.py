from __future__ import annotations

from sciona.ghost.abstract import AbstractArray


def witness_sub_graph_embedder(
    current_graph: AbstractArray,
    subgraph_quantity: int,
) -> AbstractArray:
    """Ghost witness for sub-graph embedding."""
    n = max(0, int(subgraph_quantity))
    return AbstractArray(shape=(n, 2), dtype="int64")


def witness_graph_transformer(
    current_graph: AbstractArray,
    lattice: AbstractArray,
    mapping: AbstractArray,
) -> AbstractArray:
    """Ghost witness for graph transformation."""
    return AbstractArray(shape=current_graph.shape, dtype="float32")


def witness_quantum_mwis_solver(
    graph: AbstractArray,
    lattice_id_coord_dic: AbstractArray,
    mis_sample_quantity: int,
) -> AbstractArray:
    """Ghost witness for MWIS solution samples."""
    n_samples = max(0, int(mis_sample_quantity))
    return AbstractArray(shape=(n_samples, graph.shape[0] if graph.shape else 0), dtype="int64")
