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
    / "pulsar_folding_remainder.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_pulsar_folding_remainder_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_pulsar_folding_remainder_fixture_surfaces_algorithmic_metadata() -> None:
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

    assert fixture["modules"] == ["sciona.atoms.physics.pulsar_folding.atoms"]
    assert sorted(expressions) == [
        "dm_can_brute_force",
        "spline_bandpass_correction",
    ]

    brute_force = expressions["dm_can_brute_force"]
    assert brute_force["raw_formula"] == (
        "Eq(snr, shifted_mean/(epsilon + shifted_std))"
    )
    assert brute_force["constants"] == {"epsilon": 1e-15}
    assert brute_force["mechanism_tags"] == [
        "pulsar_search",
        "shift_search",
        "signal_processing",
    ]
    assert brute_force["behavioral_archetypes"] == [
        "argmax_selection",
        "snr_scoring",
    ]
    assert variables[("dm_can_brute_force", "best_profile")][
        "variable_role"
    ] == "output"
    assert variables[("dm_can_brute_force", "epsilon")][
        "variable_role"
    ] == "constant"
    assert bounds[("dm_can_brute_force", "shifted_std")][
        "validity_statement"
    ] == "shifted_std >= 0.0"

    bandpass = expressions["spline_bandpass_correction"]
    assert bandpass["raw_formula"] == "Eq(corrected_sample, -baseline_sample + raw_sample)"
    assert bandpass["mechanism_tags"] == [
        "bandpass_correction",
        "instrumental_baseline",
        "signal_processing",
    ]
    assert bandpass["behavioral_archetypes"] == [
        "baseline_subtraction",
        "spline_smoothing",
    ]
    assert variables[("spline_bandpass_correction", "baseline_sample")][
        "variable_role"
    ] == "parameter"
    assert variables[("spline_bandpass_correction", "corrected_sample")][
        "variable_role"
    ] == "output"
    assert bounds[("spline_bandpass_correction", "sample_index")][
        "validity_statement"
    ] == "sample_index >= 0.0"


def test_pulsar_folding_remainder_fixture_loads_through_matcher_loader() -> None:
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
    assert len(rows["artifact_symbolic_variables"]) == 12
    assert len(rows["artifact_validity_bounds"]) == 4
