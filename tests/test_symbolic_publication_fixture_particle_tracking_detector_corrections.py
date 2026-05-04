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
    / "particle_tracking_detector_corrections.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_detector_corrections_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_detector_corrections_fixture_surfaces_geometry_metadata() -> None:
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
        "sciona.atoms.particle_tracking.detector_corrections.atoms"
    ]
    assert sorted(expressions) == [
        "coordinate_rescaling_for_knn",
        "perturbative_cap_correction",
        "perturbative_cylinder_correction",
    ]

    rescaling = expressions["coordinate_rescaling_for_knn"]
    assert rescaling["raw_formula"] == "Eq(x_scaled, cyl_mean_r2*x*z_scale/r_xy)"
    assert rescaling["dim_signature"]["x_scaled"] == "L1"
    assert rescaling["dim_signature"]["z_scale"] == "1"
    assert rescaling["mechanism_tags"] == [
        "detector_geometry",
        "knn_search",
        "particle_tracking",
    ]
    assert rescaling["behavioral_archetypes"] == [
        "coordinate_rescaling",
        "radius_normalization",
    ]
    assert variables[("coordinate_rescaling_for_knn", "x_scaled")][
        "variable_role"
    ] == "output"
    assert bounds[("coordinate_rescaling_for_knn", "r_xy")][
        "validity_statement"
    ] == "r_xy >= 0.0"

    cap = expressions["perturbative_cap_correction"]
    assert cap["raw_formula"] == (
        "Eq(xi_corrected, "
        "charge_sign*(dp0_radial*ur_x + dp1_azimuthal*uphi_x)/hel_p_abs + xi)"
    )
    assert cap["dim_signature"]["dp0_radial"] == "L2"
    assert cap["dim_signature"]["hel_p_abs"] == "L1"
    assert cap["behavioral_archetypes"] == [
        "azimuthal_radial_correction",
        "perturbative_update",
    ]
    assert variables[("perturbative_cap_correction", "xi_corrected")][
        "variable_role"
    ] == "output"
    assert bounds[("perturbative_cap_correction", "hel_p_abs")][
        "validity_statement"
    ] == "hel_p_abs >= 0.0"

    cylinder = expressions["perturbative_cylinder_correction"]
    assert cylinder["raw_formula"] == (
        "Eq(zi_corrected, charge_sign*dp0_z/curvature_radius + zi)"
    )
    assert cylinder["dim_signature"]["curvature_radius"] == "L1"
    assert cylinder["dim_signature"]["dp0_z"] == "L2"
    assert cylinder["behavioral_archetypes"] == [
        "curvature_scaled_update",
        "perturbative_update",
    ]
    assert bounds[("perturbative_cylinder_correction", "hel_r")][
        "validity_statement"
    ] == "hel_r >= 0.0"


def test_detector_corrections_fixture_loads_through_matcher_loader() -> None:
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
    assert len(rows["artifact_symbolic_expressions"]) == 3
    assert len(rows["artifact_symbolic_variables"]) == 33
    assert len(rows["artifact_validity_bounds"]) == 5
