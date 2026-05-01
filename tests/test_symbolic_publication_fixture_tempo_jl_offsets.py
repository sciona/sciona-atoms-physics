from __future__ import annotations

import json
from pathlib import Path

from sciona.atoms.physics.symbolic_publication_manifest import (
    build_symbolic_publication_manifest,
)
from sciona.physics_ingest.publication import load_symbolic_publication_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "data"
    / "publication_fixtures"
    / "tempo_jl_offsets.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_tempo_jl_offsets_fixture_surfaces_symbolic_review_metadata() -> None:
    fixture = _fixture()
    expressions = {
        row["atom_name"]: row for row in fixture["artifact_symbolic_expressions"]
    }
    variables = {
        (row["atom_name"], row["symbol_name"]): row
        for row in fixture["artifact_symbolic_variables"]
    }

    assert fixture["provider"] == "sciona-atoms-physics"
    assert fixture["modules"] == ["sciona.atoms.physics.tempo_jl.offsets.atoms"]
    assert fixture["artifact_validity_bounds"] == []
    assert sorted(expressions) == [
        "offset_tt2tdb",
        "offset_tt2tdbh",
        "tt2tdb_offset",
    ]

    low_order = expressions["offset_tt2tdb"]
    assert low_order["raw_formula"] == (
        "Eq(offset, k*sin(eb*sin(m0 + m1*seconds) + m0 + m1*seconds))"
    )
    assert low_order["constants"] == {
        "eb": 0.01671,
        "k": 0.001657,
        "m0": 6.239996,
        "m1": 1.99096871e-07,
    }
    assert low_order["bibliography"] == ["iau2006sofa", "repo_tempo_jl"]
    assert low_order["mechanism_tags"] == [
        "relativistic_timing",
        "time_scale_conversion",
    ]
    assert low_order["behavioral_archetypes"] == [
        "periodic_correction",
        "time_offset",
    ]
    assert low_order["dim_signature"] == {
        "eb": "1",
        "k": "T1",
        "m0": "1",
        "m1": "T-1",
        "offset": "T1",
        "seconds": "T1",
    }
    assert variables[("offset_tt2tdb", "seconds")]["variable_role"] == "input"
    assert variables[("offset_tt2tdb", "offset")]["variable_role"] == "output"
    assert variables[("offset_tt2tdb", "k")]["variable_role"] == "constant"
    assert variables[("offset_tt2tdb", "m1")]["dim_signature"] == "T-1"

    high_order = expressions["offset_tt2tdbh"]
    assert high_order["raw_formula"] == (
        "Eq(offset, a1*sin(p1 + seconds*w1/century_to_seconds) + "
        "a2*sin(p2 + seconds*w2/century_to_seconds) + "
        "a3*sin(p3 + seconds*w3/century_to_seconds) + "
        "a4*sin(p4 + seconds*w4/century_to_seconds) + "
        "a5*sin(p5 + seconds*w5/century_to_seconds) + "
        "a6*sin(p6 + seconds*w6/century_to_seconds) + "
        "a7*seconds*sin(p7 + seconds*w1/century_to_seconds)/century_to_seconds)"
    )
    assert high_order["constants"]["century_to_seconds"] == 3155760000.0
    assert high_order["constants"]["w3"] == 1256.6152
    assert high_order["constants"]["p7"] == 4.249
    assert high_order["dim_signature"]["a7"] == "T1"
    assert high_order["dim_signature"]["century_to_seconds"] == "T1"
    assert high_order["dim_signature"]["w1"] == "1"
    assert high_order["dim_signature"]["offset"] == "T1"
    assert variables[("offset_tt2tdbh", "century_to_seconds")][
        "variable_role"
    ] == "constant"
    assert variables[("offset_tt2tdbh", "seconds")]["dimension_source"] == "source"

    vectorized = expressions["tt2tdb_offset"]
    assert vectorized["raw_formula"] == low_order["raw_formula"]
    assert vectorized["constants"] == low_order["constants"]
    assert vectorized["dim_signature"] == low_order["dim_signature"]
    assert vectorized["canonical_expr_hash"] == low_order["canonical_expr_hash"]


def test_tempo_jl_offsets_fixture_matches_live_symbolic_manifest() -> None:
    fixture = _fixture()
    source = _source_manifest()

    assert fixture["artifact_symbolic_expressions"] == source[
        "artifact_symbolic_expressions"
    ]
    assert fixture["artifact_symbolic_variables"] == source[
        "artifact_symbolic_variables"
    ]
    assert fixture["artifact_validity_bounds"] == source[
        "artifact_validity_bounds"
    ]


def test_tempo_jl_offsets_fixture_loads_without_database_io() -> None:
    fixture = _fixture()
    artifact_ids = {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-00000000000{index}",
            "version_id": f"30000000-0000-0000-0000-00000000000{index}",
        }
        for index, row in enumerate(
            fixture["artifact_symbolic_expressions"],
            start=1,
        )
    }
    result = load_symbolic_publication_manifest(fixture, artifact_ids)

    assert result.diagnostics == ()
    rows = result.to_insert_rows()
    assert len(rows["artifact_symbolic_expressions"]) == 3
    assert len(rows["artifact_symbolic_variables"]) == 35
    assert len(rows["artifact_validity_bounds"]) == 0
    assert {
        row["raw_formula"] for row in rows["artifact_symbolic_expressions"]
    } == {
        "Eq(offset, k*sin(eb*sin(m0 + m1*seconds) + m0 + m1*seconds))",
        (
            "Eq(offset, a1*sin(p1 + seconds*w1/century_to_seconds) + "
            "a2*sin(p2 + seconds*w2/century_to_seconds) + "
            "a3*sin(p3 + seconds*w3/century_to_seconds) + "
            "a4*sin(p4 + seconds*w4/century_to_seconds) + "
            "a5*sin(p5 + seconds*w5/century_to_seconds) + "
            "a6*sin(p6 + seconds*w6/century_to_seconds) + "
            "a7*seconds*sin(p7 + seconds*w1/century_to_seconds)/century_to_seconds)"
        ),
    }
