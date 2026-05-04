from __future__ import annotations

import numpy as np
import sympy as sp

from sciona.atoms.physics.pulsar_folding.atoms import dm_can_brute_force, spline_bandpass_correction
from sciona.atoms.physics.pulsar_folding.dm_can import dm_candidate_filter
from sciona.atoms.physics.pulsar_folding.dm_can_witnesses import witness_dm_candidate_filter
from sciona.ghost.dimensions import DimensionalSignature
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import REGISTRY


def test_dm_can_brute_force_returns_the_input_when_all_rolls_tie() -> None:
    data = np.array([2.0, 1.0, 3.0], dtype=np.float64)

    result = dm_can_brute_force(data)

    assert np.array_equal(result, data)


def test_spline_bandpass_correction_removes_constant_baseline() -> None:
    data = np.full(4, 5.0, dtype=np.float64)

    result = spline_bandpass_correction(data)

    assert result.shape == data.shape
    assert np.allclose(result, np.zeros_like(data))


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


def test_dm_candidate_filter_registers_dispersion_delay_symbolic_metadata() -> None:
    entry = REGISTRY["dm_candidate_filter"]
    symbolic = entry["symbolic"]

    assert symbolic is not None
    assert symbolic.constants == {"K": 4.148808e3}
    assert entry["dim_signature"]["DM"] == DimensionalSignature(L=-2)
    assert symbolic.validity_bounds["DM"] == (0.0, None)
    assert symbolic.validity_bounds["candidates"] == (0.0, None)
    assert symbolic.validity_bounds["fchan"] == (0.0, None)
    assert symbolic.validity_bounds["sens"] == (0.0, None)
    assert symbolic.validity_bounds["width"] == (0.0, None)
    assert symbolic.validity_bounds["tsamp"] == (0.0, None)
    assert symbolic.check_dimensional_consistency() == []

    equation = symbolic.to_sympy()
    K, DM, fchan = sp.symbols("K DM fchan")
    assert str(equation.lhs) == "delay"
    assert sp.simplify(equation.rhs - K * DM * fchan**-2) == 0


def test_pulsar_folding_remainder_atoms_register_symbolic_metadata() -> None:
    brute_force = REGISTRY["dm_can_brute_force"]["symbolic"]
    bandpass = REGISTRY["spline_bandpass_correction"]["symbolic"]

    assert brute_force is not None
    assert brute_force.constants == {"epsilon": 1e-15}
    assert brute_force.validity_bounds["shifted_std"] == (0.0, None)
    assert brute_force.check_dimensional_consistency() == []
    shifted_mean, shifted_std, epsilon = sp.symbols(
        "shifted_mean shifted_std epsilon"
    )
    assert str(brute_force.to_sympy().lhs) == "snr"
    assert (
        sp.simplify(
            brute_force.to_sympy().rhs
            - shifted_mean / (shifted_std + epsilon)
        )
        == 0
    )

    assert bandpass is not None
    assert bandpass.validity_bounds["sample_index"] == (0.0, None)
    assert bandpass.check_dimensional_consistency() == []
    raw_sample, baseline_sample = sp.symbols("raw_sample baseline_sample")
    assert str(bandpass.to_sympy().lhs) == "corrected_sample"
    assert (
        sp.simplify(
            bandpass.to_sympy().rhs
            - (raw_sample - baseline_sample)
        )
        == 0
    )


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
