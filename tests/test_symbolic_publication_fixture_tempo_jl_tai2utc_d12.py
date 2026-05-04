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
    / "tempo_jl_tai2utc_d12.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_tai2utc_d12_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_tai2utc_d12_fixture_surfaces_leap_second_metadata() -> None:
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

    assert fixture["modules"] == ["sciona.atoms.physics.tempo_jl.tai2utc_d12.atoms"]
    assert sorted(expressions) == [
        "tai_to_utc_inversion",
        "utc_to_tai_leap_second_kernel",
    ]

    forward = expressions["utc_to_tai_leap_second_kernel"]
    assert forward["raw_formula"] == (
        "Eq(tai_total, utc1 + utc2 + delta_at/day_seconds)"
    )
    assert forward["constants"] == {"day_seconds": 86400.0}
    assert forward["dim_signature"]["delta_at"] == "T1"
    assert forward["dim_signature"]["day_seconds"] == "1"
    assert forward["mechanism_tags"] == [
        "leap_second",
        "tai_utc_conversion",
        "time_scale_conversion",
    ]
    assert forward["behavioral_archetypes"] == [
        "inverse_time_mapping",
        "leap_offset",
    ]
    assert variables[("utc_to_tai_leap_second_kernel", "tai_total")][
        "variable_role"
    ] == "output"
    assert bounds[("utc_to_tai_leap_second_kernel", "delta_at")][
        "validity_statement"
    ] == "delta_at >= 0.0"

    inverse = expressions["tai_to_utc_inversion"]
    assert inverse["raw_formula"] == (
        "Eq(candidate_utc, tai1 + tai2 - delta_at/day_seconds)"
    )
    assert inverse["constants"] == {"day_seconds": 86400.0}
    assert inverse["dim_signature"]["candidate_utc"] == "T1"
    assert variables[("tai_to_utc_inversion", "candidate_utc")][
        "variable_role"
    ] == "output"
    assert bounds[("tai_to_utc_inversion", "day_seconds")][
        "validity_statement"
    ] == "day_seconds >= 1.0"


def test_tai2utc_d12_fixture_loads_through_matcher_loader() -> None:
    fixture = _fixture()
    artifact_bindings = {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-00000000000{index}",
            "version_id": f"30000000-0000-0000-0000-00000000000{index}",
        }
        for index, row in enumerate(fixture["artifact_symbolic_expressions"], start=1)
    }

    result = load_symbolic_publication_manifest(fixture, artifact_bindings)

    assert result.diagnostics == ()
    rows = result.to_insert_rows()
    assert len(rows["artifact_symbolic_expressions"]) == 2
    assert len(rows["artifact_symbolic_variables"]) == 15
    assert len(rows["artifact_validity_bounds"]) == 4
