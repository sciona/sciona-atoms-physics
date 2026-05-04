from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import numpy as np

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND
from sciona.ghost.registry import REGISTRY


def _load_tempo_symbolic_atoms() -> None:
    importlib.import_module("sciona.atoms.physics.tempo_jl.atoms")
    importlib.import_module("sciona.atoms.physics.tempo_jl.apply_offsets.atoms")
    importlib.import_module("sciona.atoms.physics.tempo_jl.offsets.atoms")


class _JuliaMainStub:
    def eval(self, expression: str) -> object:
        raise RuntimeError(f"Julia FFI is unavailable in metadata tests: {expression}")


def _load_tai2utc_d12_symbolic_atoms() -> None:
    sys.modules.setdefault("juliacall", SimpleNamespace(Main=_JuliaMainStub()))
    importlib.import_module("sciona.atoms.physics.tempo_jl.tai2utc_d12.atoms")


def _load_find_year_symbolic_atoms() -> None:
    sys.modules.setdefault("juliacall", SimpleNamespace(Main=_JuliaMainStub()))
    importlib.import_module("sciona.atoms.physics.tempo_jl.find_year.atoms")


def _load_utc2tai_symbolic_atoms() -> None:
    sys.modules.setdefault("juliacall", SimpleNamespace(Main=_JuliaMainStub()))
    importlib.import_module("sciona.atoms.physics.tempo_jl.utc2tai.atoms")


def _load_tai2utc_symbolic_atoms() -> None:
    sys.modules.setdefault("juliacall", SimpleNamespace(Main=_JuliaMainStub()))
    importlib.import_module("sciona.atoms.physics.tempo_jl.tai2utc.atoms")


def _load_constructor_symbolic_atoms(module: str) -> None:
    sys.modules.setdefault("juliacall", SimpleNamespace(Main=_JuliaMainStub()))
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        importlib.import_module(module)


def test_tempo_offset_atoms_register_symbolic_metadata() -> None:
    _load_tempo_symbolic_atoms()

    for name in {
        "_zero_offset",
        "apply_offsets",
        "graph_time_scale_management",
        "high_precision_duration",
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

    graph_dims = REGISTRY["graph_time_scale_management"]["dim_signature"]
    assert graph_dims["source_time"] == SECOND
    assert graph_dims["target_time"] == SECOND

    duration_dims = REGISTRY["high_precision_duration"]["dim_signature"]
    assert duration_dims["duration"] == SECOND
    assert duration_dims["integer_duration"] == SECOND
    assert duration_dims["fractional_duration"] == SECOND


def test_tempo_symbolic_migration_preserves_offset_runtime_behavior() -> None:
    _load_tempo_symbolic_atoms()
    apply_offsets = REGISTRY["apply_offsets"]["impl"]
    zero_offset = REGISTRY["_zero_offset"]["impl"]
    offset_tt2tdb = REGISTRY["offset_tt2tdb"]["impl"]
    tt2tdb_offset = REGISTRY["tt2tdb_offset"]["impl"]
    graph_time_scale_management = REGISTRY["graph_time_scale_management"]["impl"]
    high_precision_duration = REGISTRY["high_precision_duration"]["impl"]

    assert zero_offset(42.5) == 0.0
    assert apply_offsets(10.0, 1.25, 0.5) == 10.75

    seconds = np.array([0.0, 1.0, 2.0])
    vectorized = tt2tdb_offset(seconds)
    scalarized = np.array([offset_tt2tdb(float(value)) for value in seconds])
    np.testing.assert_allclose(vectorized, scalarized)

    data = np.array([1.25, 2.75])
    np.testing.assert_allclose(graph_time_scale_management(data), data)
    np.testing.assert_allclose(
        high_precision_duration(data),
        np.array([[1.0, 2.0], [0.25, 0.75]]),
    )


def test_tempo_symbolic_metadata_records_constants_and_bibliography() -> None:
    _load_tempo_symbolic_atoms()

    low_order = REGISTRY["offset_tt2tdb"]["symbolic"]
    assert low_order.constants["k"] == 1.657e-3
    assert low_order.constants["m1"] == 1.99096871e-7
    assert low_order.bibliography == ["iau2006sofa", "repo_tempo_jl"]

    zero = REGISTRY["_zero_offset"]["symbolic"]
    assert zero.constants["zero_offset"] == 0.0
    assert zero.variables["offset"] == "output"

    graph = REGISTRY["graph_time_scale_management"]["symbolic"]
    assert graph.bibliography == ["urban2013almanac", "repo_tempo_jl"]
    assert graph.variables["target_time"] == "output"

    duration = REGISTRY["high_precision_duration"]["symbolic"]
    assert duration.variables["fractional_duration"] == "output"
    assert duration.validity_bounds["fractional_duration"] == (0.0, 1.0)


def test_tai2utc_d12_atoms_register_symbolic_metadata() -> None:
    _load_tai2utc_d12_symbolic_atoms()

    forward = REGISTRY["utc_to_tai_leap_second_kernel"]["symbolic"]
    inverse = REGISTRY["tai_to_utc_inversion"]["symbolic"]

    assert forward is not None
    assert forward.constants["day_seconds"] == 86400.0
    assert forward.variables["tai_total"] == "output"
    assert forward.validity_bounds["delta_at"] == (0.0, None)
    assert forward.check_dimensional_consistency() == []

    assert inverse is not None
    assert inverse.constants["day_seconds"] == 86400.0
    assert inverse.variables["candidate_utc"] == "output"
    assert inverse.validity_bounds["day_seconds"] == (1.0, None)
    assert inverse.check_dimensional_consistency() == []


def test_tempo_find_year_atoms_register_symbolic_metadata() -> None:
    _load_find_year_symbolic_atoms()

    hms = REGISTRY["hms2fd"]["symbolic"]
    cal = REGISTRY["cal2jd"]["symbolic"]
    utc = REGISTRY["utc2tai"]["symbolic"]

    assert hms is not None
    assert hms.constants["day_seconds"] == 86400.0
    assert hms.variables["fd"] == "output"
    assert hms.validity_bounds["fd"] == (0.0, 1.0)
    assert hms.check_dimensional_consistency() == []

    assert cal is not None
    assert cal.constants["jd_epoch"] == 2451545.0
    assert cal.variables["julian_day"] == "output"
    assert cal.validity_bounds["M"] == (1.0, 12.0)
    assert cal.check_dimensional_consistency() == []

    assert utc is not None
    assert utc.constants["day_seconds"] == 86400.0
    assert utc.variables["delta_at"] == "parameter"
    assert utc.dim_map["delta_at"] == SECOND
    assert utc.check_dimensional_consistency() == []


def test_tempo_utc2tai_atoms_register_symbolic_metadata() -> None:
    _load_utc2tai_symbolic_atoms()

    hms = REGISTRY["hms2fd"]["symbolic"]
    cal = REGISTRY["cal2jd"]["symbolic"]
    utc = REGISTRY["utc2tai"]["symbolic"]

    assert REGISTRY["hms2fd"]["module"].endswith("tempo_jl.utc2tai.atoms")
    assert hms is not None
    assert hms.constants["day_seconds"] == 86400.0
    assert hms.variables["fd"] == "output"
    assert hms.check_dimensional_consistency() == []

    assert cal is not None
    assert cal.constants["jd_epoch"] == 2451545.0
    assert cal.variables["julian_day"] == "output"
    assert cal.check_dimensional_consistency() == []

    assert utc is not None
    assert utc.constants["day_seconds"] == 86400.0
    assert utc.variables["tai_total"] == "output"
    assert utc.dim_map["delta_at"] == SECOND
    assert utc.check_dimensional_consistency() == []


def test_tempo_tai2utc_atoms_register_symbolic_metadata() -> None:
    _load_tai2utc_symbolic_atoms()

    hms = REGISTRY["hms2fd"]["symbolic"]
    cal = REGISTRY["cal2jd"]["symbolic"]
    inverse = REGISTRY["tai2utc"]["symbolic"]

    assert REGISTRY["hms2fd"]["module"].endswith("tempo_jl.tai2utc.atoms")
    assert hms is not None
    assert hms.constants["day_seconds"] == 86400.0
    assert hms.variables["fd"] == "output"
    assert hms.check_dimensional_consistency() == []

    assert cal is not None
    assert cal.constants["jd_epoch"] == 2451545.0
    assert cal.variables["julian_day"] == "output"
    assert cal.check_dimensional_consistency() == []

    assert inverse is not None
    assert inverse.constants["day_seconds"] == 86400.0
    assert inverse.variables["utc_total"] == "output"
    assert inverse.dim_map["delta_at"] == SECOND
    assert inverse.check_dimensional_consistency() == []


def test_tempo_constructor_modules_only_mark_equations_symbolic() -> None:
    for module in (
        "sciona.atoms.physics.tempo_jl.find_month.atoms",
        "sciona.atoms.physics.tempo_jl.jd2cal.atoms",
    ):
        _load_constructor_symbolic_atoms(module)

        date_from_offset = REGISTRY["date_from_offset"]["symbolic"]
        time_from_secondinday = REGISTRY["time_from_secondinday"]["symbolic"]
        datetime_from_seconds = REGISTRY["datetime_from_seconds"]["symbolic"]

        assert REGISTRY["date_from_offset"]["module"] == module
        assert date_from_offset is not None
        assert date_from_offset.variables["offset"] == "input"
        assert date_from_offset.variables["day"] == "output"
        assert date_from_offset.check_dimensional_consistency() == []

        assert time_from_secondinday is not None
        assert time_from_secondinday.constants["hour_seconds"] == 3600.0
        assert time_from_secondinday.dim_map["secondinday"] == SECOND
        assert time_from_secondinday.variables["s"] == "output"
        assert time_from_secondinday.check_dimensional_consistency() == []

        assert datetime_from_seconds is not None
        assert datetime_from_seconds.constants["jd_epoch"] == 2451545.0
        assert datetime_from_seconds.variables["seconds"] == "input"
        assert datetime_from_seconds.variables["Y"] == "output"
        assert datetime_from_seconds.check_dimensional_consistency() == []

        for non_equation_name in {
            "show_date",
            "show_time",
            "time_from_hms",
            "datetime_from_components",
            "datetime_from_string",
        }:
            entry = REGISTRY[non_equation_name]
            assert entry["module"] == module
            assert entry["symbolic"] is None
