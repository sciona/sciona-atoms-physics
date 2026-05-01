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
    / "tempo_jl_apply_offsets.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_tempo_jl_apply_offsets_fixture_surfaces_symbolic_metadata() -> None:
    fixture = _fixture()
    expressions = {
        row["atom_name"]: row for row in fixture["artifact_symbolic_expressions"]
    }
    variables = {
        (row["atom_name"], row["symbol_name"]): row
        for row in fixture["artifact_symbolic_variables"]
    }

    assert fixture["provider"] == "sciona-atoms-physics"
    assert fixture["modules"] == [
        "sciona.atoms.physics.tempo_jl.apply_offsets.atoms"
    ]
    assert fixture["artifact_validity_bounds"] == []
    assert sorted(expressions) == ["_zero_offset", "apply_offsets"]

    zero_offset = expressions["_zero_offset"]
    assert zero_offset["raw_formula"] == "Eq(offset, zero_offset)"
    assert zero_offset["constants"] == {"zero_offset": 0.0}
    assert zero_offset["bibliography"] == ["iau2006sofa", "repo_tempo_jl"]
    assert zero_offset["mechanism_tags"] == [
        "relativistic_timing",
        "time_scale_conversion",
    ]
    assert zero_offset["behavioral_archetypes"] == [
        "periodic_correction",
        "time_offset",
    ]
    assert zero_offset["dim_signature"] == {
        "offset": "T1",
        "seconds": "T1",
        "zero_offset": "T1",
    }
    assert variables[("_zero_offset", "seconds")]["variable_role"] == "input"
    assert variables[("_zero_offset", "offset")]["variable_role"] == "output"
    assert variables[("_zero_offset", "zero_offset")]["variable_role"] == "constant"

    apply_offsets = expressions["apply_offsets"]
    assert apply_offsets["raw_formula"] == "Eq(result, sec + ts1 - ts2)"
    assert apply_offsets["constants"] == {}
    assert apply_offsets["variables"] == {
        "result": "output",
        "sec": "input",
        "ts1": "input",
        "ts2": "input",
    }
    assert set(apply_offsets["dim_signature"].values()) == {"T1"}
    assert variables[("apply_offsets", "result")]["variable_role"] == "output"
    assert variables[("apply_offsets", "ts2")]["dimension_source"] == "source"


def test_tempo_jl_apply_offsets_fixture_matches_live_symbolic_manifest() -> None:
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


def test_tempo_jl_apply_offsets_fixture_loads_without_database_io() -> None:
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
    assert len(rows["artifact_symbolic_expressions"]) == 2
    assert len(rows["artifact_symbolic_variables"]) == 7
    assert len(rows["artifact_validity_bounds"]) == 0
    assert {
        row["raw_formula"] for row in rows["artifact_symbolic_expressions"]
    } == {
        "Eq(offset, zero_offset)",
        "Eq(result, sec + ts1 - ts2)",
    }
