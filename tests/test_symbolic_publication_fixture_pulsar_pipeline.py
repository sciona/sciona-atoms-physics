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
    / "pulsar_pipeline.publication_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_pulsar_pipeline_publication_fixture_matches_symbolic_manifest() -> None:
    assert _fixture() == _source_manifest()


def test_pulsar_pipeline_fixture_surfaces_pipeline_metadata() -> None:
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

    assert fixture["modules"] == ["sciona.atoms.physics.pulsar.pipeline"]
    assert sorted(expressions) == [
        "SNR",
        "de_disperse",
        "delay_from_DM",
        "fold_signal",
    ]

    delay = expressions["delay_from_DM"]
    assert delay["raw_formula"] == "Eq(delay, DM*K/freq_emitted**2)"
    assert delay["constants"]["K"] == 1.0 / 0.000241
    assert delay["dim_signature"]["delay"] == "T1"
    assert delay["dim_signature"]["DM"] == "L-2"
    assert delay["dim_signature"]["freq_emitted"] == "T-1"
    assert delay["mechanism_tags"] == [
        "dispersion_measure",
        "pulsar_timing",
        "signal_propagation",
    ]
    assert delay["behavioral_archetypes"] == [
        "delay_model",
        "inverse_square_scaling",
    ]
    assert variables[("delay_from_DM", "delay")]["variable_role"] == "output"
    assert variables[("delay_from_DM", "freq_emitted")][
        "variable_role"
    ] == "input"
    assert bounds[("delay_from_DM", "DM")]["validity_statement"] == "DM >= 0.0"

    dedisperse = expressions["de_disperse"]
    assert dedisperse["raw_formula"] == "Eq(shift_samples, delay/tsamp)"
    assert dedisperse["dim_signature"]["shift_samples"] == "1"
    assert dedisperse["dim_signature"]["delay"] == "T1"
    assert dedisperse["dim_signature"]["tsamp"] == "T1"
    assert dedisperse["behavioral_archetypes"] == [
        "delay_alignment",
        "time_series_shift",
    ]

    fold = expressions["fold_signal"]
    assert fold["raw_formula"] == "Eq(profile_phase, folded_sum/(multiples*n_chans))"
    assert fold["behavioral_archetypes"] == ["phase_folding", "windowed_average"]
    assert bounds[("fold_signal", "period")]["validity_statement"] == (
        "period >= 1.0"
    )

    snr = expressions["SNR"]
    assert snr["raw_formula"] == "Eq(snr, log(peak/avg_noise))"
    assert snr["mechanism_tags"] == [
        "noise_model",
        "signal_detection",
        "signal_processing",
    ]
    assert snr["behavioral_archetypes"] == ["log_ratio", "peak_to_background"]


def test_pulsar_pipeline_publication_fixture_loads_through_matcher_loader() -> None:
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
    assert len(result.to_insert_rows()["artifact_symbolic_expressions"]) == 4
