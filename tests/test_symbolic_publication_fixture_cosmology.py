from __future__ import annotations

import json
from pathlib import Path

from sciona.atoms.physics.symbolic_publication_manifest import (
    build_symbolic_publication_manifest,
)
from sciona.physics_ingest.publication import load_symbolic_publication_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT / "data" / "publication_fixtures" / "cosmology.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_cosmology_publication_fixture_matches_symbolic_manifest() -> None:
    fixture = _fixture()
    assert fixture == build_symbolic_publication_manifest(
        modules=tuple(fixture["modules"])
    )


def test_cosmology_publication_fixture_surfaces_k_correction_metadata() -> None:
    fixture = _fixture()
    expressions = {
        row["atom_name"]: row for row in fixture["artifact_symbolic_expressions"]
    }
    variables = {
        (row["atom_name"], row["symbol"]): row
        for row in fixture["artifact_symbolic_variables"]
    }
    bounds = {
        (row["atom_name"], row["symbol"]): row
        for row in fixture["artifact_validity_bounds"]
    }

    assert fixture["modules"] == ["sciona.atoms.physics.cosmology.atoms"]
    assert sorted(expressions) == ["flux_k_correction"]

    correction = expressions["flux_k_correction"]
    assert correction["raw_formula"] == "Eq(corrected_flux, flux*(redshift + 1))"
    assert correction["bibliography"] == [
        "hogg2002distance",
        "repo_sciona_atoms_physics",
    ]
    assert correction["mechanism_tags"] == [
        "cosmological_redshift",
        "flux_correction",
        "photometry",
    ]
    assert correction["behavioral_archetypes"] == [
        "multiplicative_scaling",
        "redshift_correction",
    ]
    assert correction["dim_signature"]["flux"] == "M1T-3"
    assert correction["dim_signature"]["corrected_flux"] == "M1T-3"
    assert correction["dim_signature"]["redshift"] == "1"

    assert variables[("flux_k_correction", "flux")]["variable_role"] == "input"
    assert variables[("flux_k_correction", "redshift")]["variable_role"] == "input"
    assert variables[("flux_k_correction", "band_index")][
        "variable_role"
    ] == "parameter"
    assert variables[("flux_k_correction", "corrected_flux")][
        "variable_role"
    ] == "output"
    assert bounds[("flux_k_correction", "redshift")]["validity_statement"] == (
        "redshift >= 0.0"
    )


def test_cosmology_publication_fixture_loads_through_matcher_loader() -> None:
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
