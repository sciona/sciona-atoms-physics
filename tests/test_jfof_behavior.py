from __future__ import annotations

import numpy as np

from sciona.atoms.physics.jFOF.atoms import find_fof_clusters
from sciona.atoms.physics.jFOF.topo import topological_loss_computation
from sciona.atoms.physics.jFOF.topo_witnesses import witness_topological_loss_computation
from sciona.ghost.abstract import AbstractArray, AbstractScalar


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
