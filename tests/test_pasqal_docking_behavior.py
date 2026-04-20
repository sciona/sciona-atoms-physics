from __future__ import annotations

import importlib
import json
from pathlib import Path

import networkx as nx

from sciona.atoms.physics.pasqal import (
    MolecularDockingState,
    graph_transformer,
    quantum_mwis_solver,
    sub_graph_embedder,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_PATH = REPO_ROOT / "src/sciona/atoms/physics/pasqal/references.json"


def test_pasqal_package_exports_reviewed_docking_helpers() -> None:
    package = importlib.import_module("sciona.atoms.physics.pasqal")

    assert package.graph_transformer is graph_transformer
    assert package.quantum_mwis_solver is quantum_mwis_solver
    assert package.sub_graph_embedder is sub_graph_embedder


def test_sub_graph_embedder_returns_sorted_singleton_mappings() -> None:
    graph = nx.Graph()
    graph.add_nodes_from([9, 2, 5])

    mappings, state = sub_graph_embedder(graph, 2, MolecularDockingState())

    assert mappings == [{2: 0}, {5: 1}]
    assert state.graph is graph


def test_graph_transformer_filters_edges_against_lattice() -> None:
    current_graph = nx.Graph()
    current_graph.add_edges_from([(2, 5), (5, 9), (2, 9)])
    lattice = nx.Graph()
    lattice.add_nodes_from([0, 1, 2])
    lattice.add_edge(0, 1)

    transformed, state = graph_transformer(
        current_graph,
        lattice,
        {2: 0, 5: 1, 9: 2},
        MolecularDockingState(),
    )

    assert sorted(transformed.nodes()) == [0, 1, 2]
    assert sorted(transformed.edges()) == [(0, 1)]
    assert state.graph is transformed
    assert state.lattice is lattice


def test_pasqal_references_cover_reviewed_helpers() -> None:
    references = json.loads(REFERENCES_PATH.read_text())["atoms"]

    reviewed_prefixes = {
        "sciona.atoms.physics.pasqal.docking.graph_transformer@",
        "sciona.atoms.physics.pasqal.docking.quantum_mwis_solver@",
        "sciona.atoms.physics.pasqal.docking.sub_graph_embedder@",
    }

    for prefix in reviewed_prefixes:
        matching_keys = [key for key in references if key.startswith(prefix)]
        assert matching_keys, f"missing reference binding for {prefix}"
        for key in matching_keys:
            assert references[key]["references"][0]["ref_id"] == "moleculardocking2025"
