from __future__ import annotations

import numpy as np

from sciona.atoms.physics.jFOF.atoms import FOF_DIM_MAP
from sciona.atoms.physics.jFOF.atoms import find_fof_clusters
from sciona.atoms.physics.jFOF.topo import (
    TOPOLOGICAL_LOSS_DIM_MAP,
    topological_loss_computation,
)
from sciona.atoms.physics.jFOF.topo_witnesses import witness_topological_loss_computation
from sciona.ghost.abstract import AbstractArray, AbstractScalar
from sciona.ghost.dimensions import DIMENSIONLESS, METER
from sciona.ghost.registry import REGISTRY


def test_find_fof_clusters_groups_nearby_points() -> None:
    points = np.array(
        [
            [0.0, 0.0],
            [0.05, 0.0],
            [1.0, 1.0],
        ],
        dtype=np.float64,
    )

    labels = find_fof_clusters(points, b=0.1, L=10.0)

    assert labels.shape == (3,)
    assert labels[0] == labels[1]
    assert labels[2] != labels[0]


def test_topological_loss_computation_returns_scalar_float() -> None:
    logits = np.array([[2.0, 0.0], [0.0, 2.0]], dtype=np.float64)
    loss = topological_loss_computation(
        key=np.array([0, 1], dtype=np.int32),
        logits=logits,
        pos32=np.zeros((2, 3), dtype=np.float32),
        nbr_idx=np.array([[1], [0]], dtype=np.intp),
        b=np.array([0.1], dtype=np.float32),
        max_iters=2,
        tau=1.0,
    )

    assert isinstance(loss, float)
    assert loss > 0.0


def test_topological_loss_witness_is_scalar() -> None:
    result = witness_topological_loss_computation(
        key=AbstractArray(shape=(2,), dtype="int32"),
        logits=AbstractArray(shape=(2, 2), dtype="float64"),
        pos32=AbstractArray(shape=(2, 3), dtype="float32"),
        nbr_idx=AbstractArray(shape=(2, 1), dtype="int64"),
        b=AbstractArray(shape=(1,), dtype="float32"),
        max_iters=AbstractScalar(dtype="int64"),
        tau=AbstractScalar(dtype="float64"),
    )

    assert isinstance(result, AbstractScalar)
    assert result.dtype == "float64"


def test_jfof_registers_dimensional_metadata_without_forcing_symbolic_equations() -> None:
    cluster_entry = REGISTRY["find_fof_clusters"]
    loss_entry = REGISTRY["topological_loss_computation"]

    assert cluster_entry["symbolic"] is None
    assert loss_entry["symbolic"] is None
    assert cluster_entry["dim_signature"] == FOF_DIM_MAP
    assert loss_entry["dim_signature"] == TOPOLOGICAL_LOSS_DIM_MAP
    assert cluster_entry["dim_signature"]["x"] == METER
    assert cluster_entry["dim_signature"]["b"] == METER
    assert cluster_entry["dim_signature"]["labels"] == DIMENSIONLESS
    assert loss_entry["dim_signature"]["pos32"] == METER
    assert loss_entry["dim_signature"]["b"] == METER
    assert loss_entry["dim_signature"]["loss"] == DIMENSIONLESS


def test_jfof_symbolic_review_blockers_are_explicit() -> None:
    from sciona.atoms.physics.jFOF import atoms, topo

    assert "union-find component labels" in atoms.SYMBOLIC_REVIEW_BLOCKERS["find_fof_clusters"]
    assert "neighbor-indexed softmax" in topo.SYMBOLIC_REVIEW_BLOCKERS["topological_loss_computation"]
