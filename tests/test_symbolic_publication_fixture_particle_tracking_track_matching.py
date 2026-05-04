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
    / "particle_tracking_track_matching.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_track_matching_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_track_matching_fixture_surfaces_matching_metadata() -> None:
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

    assert fixture["modules"] == [
        "sciona.atoms.particle_tracking.track_matching.atoms"
    ]
    assert sorted(expressions) == [
        "bayesian_neighbor_evaluation",
        "greedy_track_commit",
        "helix_cap_intersection",
        "helix_cylinder_intersection",
    ]

    cylinder = expressions["helix_cylinder_intersection"]
    assert cylinder["raw_formula"] == "Eq(target_r2sqr, xi**2 + yi**2)"
    assert cylinder["dim_signature"]["target_r2sqr"] == "L2"
    assert cylinder["dim_signature"]["xi"] == "L1"
    assert cylinder["behavioral_archetypes"] == [
        "cylinder_intersection",
        "phase_advance",
    ]
    assert variables[("helix_cylinder_intersection", "target_r2sqr")][
        "variable_role"
    ] == "input"
    assert variables[("helix_cylinder_intersection", "dphi")][
        "variable_role"
    ] == "output"
    assert bounds[("helix_cylinder_intersection", "hel_r")][
        "validity_statement"
    ] == "hel_r >= 0.0"

    cap = expressions["helix_cap_intersection"]
    assert cap["raw_formula"] == "Eq(dphi, (target_z - z0)/hel_p)"
    assert cap["dim_signature"]["hel_p"] == "L1"
    assert cap["behavioral_archetypes"] == ["cap_intersection", "phase_advance"]
    assert bounds[("helix_cap_intersection", "hel_p")][
        "validity_statement"
    ] == "hel_p >= 0.0"

    bayes = expressions["bayesian_neighbor_evaluation"]
    assert bayes["raw_formula"] == (
        "Eq(de, sqrt(d_phi**2/e_phi**2 + d_theta**2/e_theta**2))"
    )
    assert bayes["mechanism_tags"] == [
        "bayesian_filtering",
        "particle_tracking",
        "track_extension",
    ]
    assert bayes["behavioral_archetypes"] == [
        "likelihood_ratio_cut",
        "normalized_distance",
    ]
    assert bounds[("bayesian_neighbor_evaluation", "e_theta")][
        "validity_statement"
    ] == "e_theta >= 0.0"

    greedy = expressions["greedy_track_commit"]
    assert greedy["raw_formula"] == "Eq(loss_fraction, nloss/nhits)"
    assert greedy["behavioral_archetypes"] == [
        "greedy_selection",
        "loss_fraction_gate",
    ]
    assert bounds[("greedy_track_commit", "loss_fraction")][
        "validity_statement"
    ] == "0.0 <= loss_fraction <= 1.0"


def test_track_matching_fixture_loads_through_matcher_loader() -> None:
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
    assert len(rows["artifact_symbolic_expressions"]) == 4
    assert len(rows["artifact_symbolic_variables"]) == 43
    assert len(rows["artifact_validity_bounds"]) == 15
