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
    / "tempo_jl_root.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_tempo_jl_root_fixture_surfaces_symbolic_metadata() -> None:
    fixture = _fixture()
    expressions = {
        row["atom_name"]: row for row in fixture["artifact_symbolic_expressions"]
    }
    variables = {
        (row["atom_name"], row["symbol_name"]): row
        for row in fixture["artifact_symbolic_variables"]
    }
    bounds = {
        (row["atom_name"], row["variable_name"]): row
        for row in fixture["artifact_validity_bounds"]
    }

    assert fixture["provider"] == "sciona-atoms-physics"
    assert fixture["modules"] == ["sciona.atoms.physics.tempo_jl.atoms"]
    assert sorted(expressions) == [
        "graph_time_scale_management",
        "high_precision_duration",
    ]

    graph = expressions["graph_time_scale_management"]
    assert graph["raw_formula"] == "Eq(target_time, source_time)"
    assert graph["bibliography"] == ["urban2013almanac", "repo_tempo_jl"]
    assert graph["mechanism_tags"] == [
        "time_scale_conversion",
        "time_scale_graph",
    ]
    assert graph["behavioral_archetypes"] == [
        "identity_mapping",
        "path_transform",
    ]
    assert graph["dim_signature"] == {
        "source_time": "T1",
        "target_time": "T1",
    }
    assert variables[("graph_time_scale_management", "source_time")][
        "variable_role"
    ] == "input"
    assert variables[("graph_time_scale_management", "target_time")][
        "variable_role"
    ] == "output"

    duration = expressions["high_precision_duration"]
    assert (
        duration["raw_formula"]
        == "Eq(duration, fractional_duration + integer_duration)"
    )
    assert duration["mechanism_tags"] == [
        "precision_management",
        "time_scale_conversion",
    ]
    assert duration["behavioral_archetypes"] == [
        "fractional_decomposition",
        "time_duration_split",
    ]
    assert duration["variables"] == {
        "duration": "input",
        "fractional_duration": "output",
        "integer_duration": "output",
    }
    assert set(duration["dim_signature"].values()) == {"T1"}
    assert bounds[("high_precision_duration", "fractional_duration")][
        "min_value"
    ] == 0.0
    assert bounds[("high_precision_duration", "fractional_duration")][
        "max_value"
    ] == 1.0


def test_tempo_jl_root_fixture_matches_live_symbolic_manifest() -> None:
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


def test_tempo_jl_root_fixture_loads_without_database_io() -> None:
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
    assert len(rows["artifact_symbolic_variables"]) == 5
    assert len(rows["artifact_validity_bounds"]) == 1
