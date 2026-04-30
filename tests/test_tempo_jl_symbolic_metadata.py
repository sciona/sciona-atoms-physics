from __future__ import annotations

import importlib

import numpy as np

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND
from sciona.ghost.registry import REGISTRY


def _load_tempo_symbolic_atoms() -> None:
    importlib.import_module("sciona.atoms.physics.tempo_jl.apply_offsets.atoms")
    importlib.import_module("sciona.atoms.physics.tempo_jl.offsets.atoms")


def test_tempo_offset_atoms_register_symbolic_metadata() -> None:
    _load_tempo_symbolic_atoms()

    for name in {
        "_zero_offset",
        "apply_offsets",
        "offset_tt2tdb",
        "offset_tt2tdbh",
        "tt2tdb_offset",
    }:
        entry = REGISTRY[name]
        symbolic = entry["symbolic"]
        assert symbolic is not None, name
        assert symbolic.check_dimensional_consistency() == []


def test_tempo_offset_dimensions_are_registered() -> None:
    _load_tempo_symbolic_atoms()

    zero_dims = REGISTRY["_zero_offset"]["dim_signature"]
    assert zero_dims["seconds"] == SECOND
    assert zero_dims["offset"] == SECOND

    apply_dims = REGISTRY["apply_offsets"]["dim_signature"]
    assert apply_dims["sec"] == SECOND
    assert apply_dims["ts1"] == SECOND
    assert apply_dims["ts2"] == SECOND
    assert apply_dims["result"] == SECOND

    low_order_dims = REGISTRY["offset_tt2tdb"]["dim_signature"]
    assert low_order_dims["seconds"] == SECOND
    assert low_order_dims["offset"] == SECOND
    assert low_order_dims["m1"] == SECOND.power(-1)
    assert low_order_dims["m0"] == DIMENSIONLESS
    assert low_order_dims["eb"] == DIMENSIONLESS

    high_order_dims = REGISTRY["offset_tt2tdbh"]["dim_signature"]
    assert high_order_dims["seconds"] == SECOND
    assert high_order_dims["century_to_seconds"] == SECOND
    assert high_order_dims["offset"] == SECOND


def test_tempo_symbolic_migration_preserves_offset_runtime_behavior() -> None:
    _load_tempo_symbolic_atoms()
    apply_offsets = REGISTRY["apply_offsets"]["impl"]
    zero_offset = REGISTRY["_zero_offset"]["impl"]
    offset_tt2tdb = REGISTRY["offset_tt2tdb"]["impl"]
    tt2tdb_offset = REGISTRY["tt2tdb_offset"]["impl"]

    assert zero_offset(42.5) == 0.0
    assert apply_offsets(10.0, 1.25, 0.5) == 10.75

    seconds = np.array([0.0, 1.0, 2.0])
    vectorized = tt2tdb_offset(seconds)
    scalarized = np.array([offset_tt2tdb(float(value)) for value in seconds])
    np.testing.assert_allclose(vectorized, scalarized)


def test_tempo_symbolic_metadata_records_constants_and_bibliography() -> None:
    _load_tempo_symbolic_atoms()

    low_order = REGISTRY["offset_tt2tdb"]["symbolic"]
    assert low_order.constants["k"] == 1.657e-3
    assert low_order.constants["m1"] == 1.99096871e-7
    assert low_order.bibliography == ["iau2006sofa", "repo_tempo_jl"]

    zero = REGISTRY["_zero_offset"]["symbolic"]
    assert zero.constants["zero_offset"] == 0.0
    assert zero.variables["offset"] == "output"
