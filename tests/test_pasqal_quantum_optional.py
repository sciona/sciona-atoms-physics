from __future__ import annotations

import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import networkx as nx
import pytest

pytest.importorskip("pulser")
pytest.importorskip("emu_sv")

from sciona.atoms.physics.pasqal import MolecularDockingState, quantum_mwis_solver


def test_pasqal_quantum_mwis_solver_uses_pulser_optional_backend() -> None:
    graph = nx.Graph()
    graph.add_node(0, weight=1.0)
    graph.add_node(1, weight=0.5)
    graph.add_edge(0, 1)
    coordinates = {0: (0.0, 0.0), 1: (6.0, 0.0)}

    solutions, state = quantum_mwis_solver(
        graph,
        coordinates,
        1,
        MolecularDockingState(),
    )

    assert len(solutions) == 1
    assert all(isinstance(solution, set) for solution in solutions)
    assert state.graph is graph
    assert state.lattice_id_coord_dic == coordinates
