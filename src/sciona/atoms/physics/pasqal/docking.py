"""Pasqal-inspired molecular docking atoms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import icontract

from sciona.ghost.registry import register_atom

from .docking_state import MolecularDockingState
from .docking_witnesses import (
    witness_graph_transformer,
    witness_quantum_mwis_solver,
    witness_sub_graph_embedder,
)
from ._pulser_optional import solve_quantum_mwis

if TYPE_CHECKING:
    import networkx as nx


def _nx() -> Any:
    import networkx as nx

    return nx


def _is_graph(value: object) -> bool:
    return isinstance(value, _nx().Graph)


@register_atom(witness_sub_graph_embedder)
@icontract.require(lambda subgraph_quantity: subgraph_quantity > 0, "subgraph_quantity must be positive")
@icontract.ensure(lambda result: isinstance(result, tuple) and len(result) == 2, "Result must be a (mappings, state) tuple")
@icontract.ensure(lambda result: isinstance(result[0], list), "First element must be a list of mappings")
def sub_graph_embedder(
    current_graph: "nx.Graph",
    subgraph_quantity: int,
    state: MolecularDockingState,
) -> tuple[list[dict[int, int]], MolecularDockingState]:
    """Extract deterministic embeddable node mappings from a graph."""
    nodes = sorted(current_graph.nodes())
    limit = min(subgraph_quantity, len(nodes))

    mappings: list[dict[int, int]] = []
    for idx in range(limit):
        mappings.append({int(nodes[idx]): idx})

    new_state = state.model_copy(update={"graph": current_graph})
    return mappings, new_state


@register_atom(witness_graph_transformer)
@icontract.require(lambda mapping: len(mapping) > 0, "mapping must not be empty")
@icontract.ensure(lambda result: isinstance(result, tuple) and len(result) == 2, "Result must be a (graph, state) tuple")
@icontract.ensure(lambda result: _is_graph(result[0]), "First element must be a networkx Graph")
def graph_transformer(
    current_graph: "nx.Graph",
    lattice: "nx.Graph",
    mapping: dict[int, int],
    state: MolecularDockingState,
) -> tuple["nx.Graph", MolecularDockingState]:
    """Map a subgraph onto lattice coordinates deterministically."""
    nx = _nx()
    transformed = nx.Graph()

    mapped_nodes = sorted(set(mapping.values()))
    transformed.add_nodes_from(mapped_nodes)

    for u, v in current_graph.edges():
        if u not in mapping or v not in mapping:
            continue
        mu = mapping[u]
        mv = mapping[v]
        if mu == mv:
            continue

        if lattice.number_of_nodes() == 0:
            transformed.add_edge(mu, mv)
        elif lattice.has_node(mu) and lattice.has_node(mv):
            if lattice.number_of_edges() == 0 or lattice.has_edge(mu, mv):
                transformed.add_edge(mu, mv)

    new_state = state.model_copy(
        update={
            "graph": transformed,
            "lattice": lattice,
        }
    )
    return transformed, new_state


@register_atom(witness_quantum_mwis_solver)
@icontract.require(lambda mis_sample_quantity: mis_sample_quantity > 0, "mis_sample_quantity must be positive")
@icontract.ensure(lambda result: isinstance(result, tuple) and len(result) == 2, "Result must be a (solutions, state) tuple")
@icontract.ensure(lambda result: isinstance(result[0], list), "First element must be a list of independent sets")
def quantum_mwis_solver(
    graph: "nx.Graph",
    lattice_id_coord_dic: dict[int, tuple[float, float]],
    mis_sample_quantity: int,
    state: MolecularDockingState,
) -> tuple[list[set[int]], MolecularDockingState]:
    """Sample MWIS candidates with the source Pulser neutral-atom adiabatic solver."""
    solutions = solve_quantum_mwis(graph, lattice_id_coord_dic, mis_sample_quantity)
    new_state = state.model_copy(
        update={
            "graph": graph,
            "lattice_id_coord_dic": lattice_id_coord_dic,
        }
    )
    return solutions, new_state
