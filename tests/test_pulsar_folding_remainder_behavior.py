from __future__ import annotations

import numpy as np

from sciona.atoms.physics.pulsar_folding.dm_can import dm_candidate_filter
from sciona.atoms.physics.pulsar_folding.dm_can_witnesses import witness_dm_candidate_filter
from sciona.ghost.abstract import AbstractArray


def test_dm_candidate_filter_returns_one_score_per_candidate() -> None:
    data = np.array([1.0, 3.0], dtype=np.float64)
    candidates = np.array([10.0, 20.0, 30.0], dtype=np.float64)

    result = dm_candidate_filter(
        data=data,
        data_base=np.zeros_like(data),
        sens=2.0,
        DM_base=0.0,
        candidates=candidates,
        fchan=100.0,
        width=1.0,
        tsamp=1.0,
    )

    assert result.shape == (3,)
    assert np.array_equal(result, np.array([1.0, 1.0, 1.0], dtype=np.float64))


def test_dm_candidate_filter_witness_tracks_candidate_count() -> None:
    result = witness_dm_candidate_filter(
        data=AbstractArray(shape=(2,), dtype="float64"),
        data_base=AbstractArray(shape=(2,), dtype="float64"),
        sens=AbstractArray(shape=(1,), dtype="float64"),
        DM_base=AbstractArray(shape=(1,), dtype="float64"),
        candidates=AbstractArray(shape=(3,), dtype="float64"),
        fchan=AbstractArray(shape=(1,), dtype="float64"),
        width=AbstractArray(shape=(1,), dtype="float64"),
        tsamp=AbstractArray(shape=(1,), dtype="float64"),
    )

    assert result.shape == (3,)
    assert result.dtype == "float64"
