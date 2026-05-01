from __future__ import annotations

import json
from pathlib import Path

from sciona.atoms.physics.symbolic_publication_manifest import (
    build_symbolic_publication_manifest,
)
from sciona.physics_ingest.publication import load_symbolic_publication_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT / "data" / "publication_fixtures" / "skyfield.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_skyfield_publication_fixture_surfaces_symbolic_review_metadata() -> None:
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
    assert fixture["modules"] == ["sciona.atoms.physics.skyfield.atoms"]
    assert sorted(expressions) == [
        "calculate_vector_angle",
        "compute_spherical_coordinate_rates",
    ]

    angle = expressions["calculate_vector_angle"]
    assert angle["raw_formula"] == (
        "Eq(cos(theta), (ux*wx + uy*wy + uz*wz)/(u_norm*w_norm))"
    )
    assert angle["bibliography"] == ["skyfield2019ascl", "repo_skyfield"]
    assert angle["mechanism_tags"] == [
        "astrometry",
        "coordinate_transform",
        "vector_geometry",
    ]
    assert angle["behavioral_archetypes"] == [
        "angular_geometry",
        "coordinate_transform",
    ]
    assert angle["dim_signature"]["theta"] == "1"
    assert angle["dim_signature"]["u_norm"] == "L1"
    assert variables[("calculate_vector_angle", "theta")][
        "variable_role"
    ] == "output"
    assert variables[("calculate_vector_angle", "u_norm")][
        "variable_role"
    ] == "parameter"
    assert bounds[("calculate_vector_angle", "theta")]["validity_statement"] == (
        "0.0 <= theta <= 3.141592653589793"
    )
    assert bounds[("calculate_vector_angle", "w_norm")]["validity_statement"] == (
        "w_norm >= 0.0"
    )

    rates = expressions["compute_spherical_coordinate_rates"]
    assert rates["raw_formula"] == "Eq(range_rate, (rx*vx + ry*vy + rz*vz)/range)"
    assert rates["bibliography"] == ["skyfield2019ascl", "repo_skyfield"]
    assert rates["mechanism_tags"] == [
        "astrometry",
        "coordinate_transform",
        "vector_geometry",
    ]
    assert rates["dim_signature"]["range"] == "L1"
    assert rates["dim_signature"]["range_rate"] == "L1T-1"
    assert rates["dim_signature"]["latitude_rate"] == "T-1"
    assert variables[("compute_spherical_coordinate_rates", "r")][
        "variable_role"
    ] == "input"
    assert variables[("compute_spherical_coordinate_rates", "range_rate")][
        "variable_role"
    ] == "output"
    assert bounds[("compute_spherical_coordinate_rates", "range")][
        "validity_statement"
    ] == "range >= 0.0"


def test_skyfield_publication_fixture_matches_live_symbolic_manifest() -> None:
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


def test_skyfield_publication_fixture_loads_without_database_io() -> None:
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
    assert len(rows["artifact_symbolic_variables"]) == 25
    assert len(rows["artifact_validity_bounds"]) == 4
    assert {
        row["raw_formula"] for row in rows["artifact_symbolic_expressions"]
    } == {
        "Eq(cos(theta), (ux*wx + uy*wy + uz*wz)/(u_norm*w_norm))",
        "Eq(range_rate, (rx*vx + ry*vy + rz*vz)/range)",
    }
