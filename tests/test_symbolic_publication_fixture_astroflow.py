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
    / "astroflow.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_astroflow_publication_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_astroflow_publication_fixture_surfaces_dedispersion_metadata() -> None:
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

    assert fixture["modules"] == ["sciona.atoms.physics.astroflow.atoms"]
    assert sorted(expressions) == ["dedispersionkernel"]

    kernel = expressions["dedispersionkernel"]
    assert kernel["raw_formula"] == "Eq(output_sample, input_sum/nchans)"
    assert kernel["bibliography"] == ["astroflow2025", "repo_astroflow"]
    assert kernel["mechanism_tags"] == [
        "dedispersion",
        "pulsar_search",
        "signal_processing",
    ]
    assert kernel["behavioral_archetypes"] == [
        "channel_aggregation",
        "delay_alignment",
    ]
    assert kernel["dim_signature"]["output_sample"] == "1"
    assert kernel["dim_signature"]["nchans"] == "1"

    assert variables[("dedispersionkernel", "output_sample")][
        "variable_role"
    ] == "output"
    assert variables[("dedispersionkernel", "input_sum")]["variable_role"] == "input"
    assert variables[("dedispersionkernel", "nchans")][
        "variable_role"
    ] == "parameter"
    assert bounds[("dedispersionkernel", "nchans")]["validity_statement"] == (
        "nchans >= 1.0"
    )
    assert bounds[("dedispersionkernel", "time_downsample")][
        "validity_statement"
    ] == "time_downsample >= 1.0"


def test_astroflow_publication_fixture_loads_through_matcher_loader() -> None:
    fixture = _fixture()
    artifact_bindings = {
        row["artifact_key"]: {
            "artifact_id": "20000000-0000-0000-0000-000000000001",
            "version_id": "30000000-0000-0000-0000-000000000001",
        }
        for row in fixture["artifact_symbolic_expressions"]
    }

    result = load_symbolic_publication_manifest(fixture, artifact_bindings)

    assert result.diagnostics == ()
    assert len(result.to_insert_rows()["artifact_symbolic_expressions"]) == 1
