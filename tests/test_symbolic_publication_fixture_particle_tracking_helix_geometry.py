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
    / "particle_tracking_helix_geometry.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_particle_tracking_helix_geometry_fixture_surfaces_symbolic_review_metadata() -> None:
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
    assert fixture["modules"] == [
        "sciona.atoms.particle_tracking.helix_geometry.atoms"
    ]
    assert sorted(expressions) == [
        "circle_from_three_points",
        "helix_direction_from_two_points",
        "helix_nearest_point_distance",
        "helix_pitch_from_two_points",
        "helix_pitch_least_squares",
    ]

    circle = expressions["circle_from_three_points"]
    assert circle["raw_formula"] == "Eq(r**2, (x1 - xm)**2 + (y1 - ym)**2)"
    assert circle["bibliography"] == ["steiner2018trackml", "amrouche2019trackml"]
    assert circle["mechanism_tags"] == [
        "geometric_reconstruction",
        "helix_geometry",
        "particle_tracking",
    ]
    assert circle["behavioral_archetypes"] == [
        "geometric_fit",
        "track_reconstruction",
    ]
    assert circle["dim_signature"]["r"] == "L1"
    assert circle["dim_signature"]["large_radius"] == "L1"
    assert variables[("circle_from_three_points", "r")]["variable_role"] == "output"
    assert variables[("circle_from_three_points", "large_radius")][
        "variable_role"
    ] == "parameter"
    assert bounds[("circle_from_three_points", "r")]["validity_statement"] == (
        "r >= 0.0"
    )

    pitch = expressions["helix_pitch_from_two_points"]
    assert pitch["raw_formula"] == "Eq(hel_pitch, 2*pi*dz/phid)"
    assert pitch["dim_signature"]["phid"] == "1"
    assert pitch["dim_signature"]["zero_pitch"] == "L1"
    assert variables[("helix_pitch_from_two_points", "phid")][
        "variable_role"
    ] == "output"
    assert bounds[("helix_pitch_from_two_points", "phid")][
        "validity_statement"
    ] == "-3.141592653589793 <= phid <= 3.141592653589793"

    nearest = expressions["helix_nearest_point_distance"]
    assert nearest["raw_formula"] == (
        "Eq(dist**2, (x - x1)**2 + (y - y1)**2 + (z - z1)**2)"
    )
    assert nearest["mechanism_tags"] == [
        "distance_minimization",
        "geometric_reconstruction",
        "helix_geometry",
        "particle_tracking",
    ]
    assert nearest["behavioral_archetypes"] == [
        "distance_minimization",
        "geometric_fit",
        "track_reconstruction",
    ]
    assert nearest["dim_signature"]["iterations"] == "1"
    assert bounds[("helix_nearest_point_distance", "iterations")][
        "validity_statement"
    ] == "iterations >= 1.0"


def test_particle_tracking_helix_geometry_fixture_matches_live_symbolic_manifest() -> None:
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


def test_particle_tracking_helix_geometry_fixture_loads_without_database_io() -> None:
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
    assert len(rows["artifact_symbolic_expressions"]) == 5
    assert len(rows["artifact_symbolic_variables"]) == 70
    assert len(rows["artifact_validity_bounds"]) == 8
    assert {
        row["raw_formula"] for row in rows["artifact_symbolic_expressions"]
    } == {
        "Eq(dist**2, (x - x1)**2 + (y - y1)**2 + (z - z1)**2)",
        "Eq(hel_dz, -z1 + z2)",
        "Eq(hel_pitch, 2*pi*dz/phid)",
        "Eq(hel_pitch, 2*pi*(-sum_phi*sum_z + 3*sum_zphi)/(-sum_phi**2 + 3*sum_phisqr))",
        "Eq(r**2, (x1 - xm)**2 + (y1 - ym)**2)",
    }
