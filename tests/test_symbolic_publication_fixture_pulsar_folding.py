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
    / "pulsar_folding_dm_candidate_filter.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_pulsar_folding_publication_fixture_surfaces_symbolic_review_metadata() -> None:
    fixture = _fixture()
    expression = fixture["artifact_symbolic_expressions"][0]
    variables = {
        row["symbol_name"]: row for row in fixture["artifact_symbolic_variables"]
    }
    bounds = {
        row["variable_name"]: row for row in fixture["artifact_validity_bounds"]
    }

    assert fixture["provider"] == "sciona-atoms-physics"
    assert fixture["modules"] == ["sciona.atoms.physics.pulsar_folding.dm_can"]
    assert expression["atom_name"] == "dm_candidate_filter"
    assert expression["raw_formula"] == "Eq(delay, DM*K/fchan**2)"
    assert expression["constants"] == {"K": 4148.808}
    assert expression["bibliography"] == [
        "lorimer2005pulsar",
        "repo_pulsar_folding",
    ]
    assert expression["mechanism_tags"] == [
        "dispersion",
        "pulsar_search",
        "signal_processing",
    ]
    assert expression["behavioral_archetypes"] == [
        "candidate_scoring",
        "delay_model",
    ]
    assert expression["dim_signature"]["DM"] == "L-2"
    assert expression["dim_signature"]["K"] == "L2T-1"
    assert expression["dim_signature"]["delay"] == "T1"
    assert expression["dim_signature"]["fchan"] == "T-1"

    assert variables["DM"]["variable_role"] == "input"
    assert variables["DM"]["dim_signature"] == "L-2"
    assert variables["K"]["variable_role"] == "constant"
    assert variables["delay"]["variable_role"] == "output"
    assert variables["fchan"]["dimension_source"] == "source"
    assert variables["DM_base"]["variable_role"] == "input"
    assert variables["candidates"]["dim_signature"] == "L-2"
    assert variables["sens"]["dim_signature"] == "1"

    assert bounds["DM"]["lower_value"] == 0.0
    assert bounds["DM"]["upper_value"] is None
    assert bounds["DM"]["validity_statement"] == "DM >= 0.0"
    assert bounds["DM_base"]["validity_statement"] == "DM_base >= 0.0"
    assert bounds["fchan"]["dim_signature"] == "T-1"


def test_pulsar_folding_publication_fixture_matches_live_symbolic_manifest() -> None:
    fixture = _fixture()
    source = _source_manifest()

    fixture_expression = fixture["artifact_symbolic_expressions"][0]
    source_expression = source["artifact_symbolic_expressions"][0]

    for field in (
        "artifact_key",
        "expression_id",
        "expression_srepr",
        "raw_formula",
        "canonical_expr_hash",
        "topology_hash",
        "dimensional_hash",
        "variables",
        "dim_signature",
        "constants",
        "bibliography",
        "mechanism_tags",
        "behavioral_archetypes",
    ):
        assert fixture_expression[field] == source_expression[field]

    source_variables = {
        row["symbol_name"]: row for row in source["artifact_symbolic_variables"]
    }
    for fixture_row in fixture["artifact_symbolic_variables"]:
        source_row = source_variables[fixture_row["symbol_name"]]
        for field in (
            "source_variable_id",
            "variable_role",
            "dim_signature",
            "dimension_source",
            "ordinal",
        ):
            assert fixture_row[field] == source_row[field]

    source_bounds = {
        row["variable_name"]: row for row in source["artifact_validity_bounds"]
    }
    for fixture_row in fixture["artifact_validity_bounds"]:
        source_row = source_bounds[fixture_row["variable_name"]]
        for field in (
            "source_bound_id",
            "scope",
            "bound_kind",
            "lower_value",
            "upper_value",
            "dim_signature",
            "validity_statement",
            "confidence",
            "review_status",
        ):
            assert fixture_row[field] == source_row[field]


def test_pulsar_folding_publication_fixture_loads_without_database_io() -> None:
    fixture = _fixture()
    artifact_key = fixture["artifact_symbolic_expressions"][0]["artifact_key"]
    result = load_symbolic_publication_manifest(
        fixture,
        {
            artifact_key: {
                "artifact_id": "20000000-0000-0000-0000-000000000001",
                "version_id": "30000000-0000-0000-0000-000000000001",
            }
        },
    )

    assert result.diagnostics == ()
    rows = result.to_insert_rows()
    assert len(rows["artifact_symbolic_expressions"]) == 1
    assert len(rows["artifact_symbolic_variables"]) == 9
    assert len(rows["artifact_validity_bounds"]) == 7
    assert rows["artifact_symbolic_expressions"][0]["mechanism_tags"] == [
        "dispersion",
        "pulsar_search",
        "signal_processing",
    ]
