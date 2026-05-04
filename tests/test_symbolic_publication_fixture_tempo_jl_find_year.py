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
    / "tempo_jl_find_year.publication_manifest.json"
)
EXPECTED_NAMES = {
    "cal2jd",
    "calhms2jd",
    "fd2hms",
    "fd2hmsf",
    "find_day",
    "find_dayinyear",
    "find_month",
    "find_year",
    "hms2fd",
    "isleapyear",
    "jd2cal",
    "jd2calhms",
    "lastj2000dayofyear",
    "tai2utc",
    "utc2tai",
}


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_manifest() -> dict:
    fixture = _fixture()
    return build_symbolic_publication_manifest(modules=tuple(fixture["modules"]))


def test_tempo_jl_find_year_fixture_surfaces_symbolic_metadata() -> None:
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
    assert fixture["modules"] == ["sciona.atoms.physics.tempo_jl.find_year.atoms"]
    assert set(expressions) == EXPECTED_NAMES

    hms = expressions["hms2fd"]
    assert (
        hms["raw_formula"]
        == "Eq(fd, (h*hour_seconds + m*minute_seconds + s)/day_seconds)"
    )
    assert hms["constants"] == {
        "day_seconds": 86400.0,
        "hour_seconds": 3600.0,
        "minute_seconds": 60.0,
    }
    assert hms["mechanism_tags"] == [
        "calendar_time",
        "time_of_day_conversion",
    ]
    assert hms["behavioral_archetypes"] == [
        "fractional_day_conversion",
        "unit_conversion",
    ]
    assert variables[("hms2fd", "s")]["dim_signature"] == "T1"
    assert variables[("hms2fd", "fd")]["variable_role"] == "output"
    assert bounds[("hms2fd", "fd")]["min_value"] == 0.0
    assert bounds[("hms2fd", "fd")]["max_value"] == 1.0

    cal = expressions["cal2jd"]
    assert cal["raw_formula"] == "Eq(julian_day, j2000_offset_day + jd_epoch)"
    assert cal["constants"]["jd_epoch"] == 2451545.0
    assert cal["mechanism_tags"] == [
        "calendar_conversion",
        "julian_date",
        "time_scale_conversion",
    ]
    assert variables[("cal2jd", "julian_day")]["variable_role"] == "output"
    assert bounds[("cal2jd", "M")]["validity_statement"] == "1.0 <= M <= 12.0"

    utc = expressions["utc2tai"]
    assert utc["raw_formula"] == "Eq(tai_total, utc1 + utc2 + delta_at/day_seconds)"
    assert utc["constants"] == {"day_seconds": 86400.0}
    assert utc["mechanism_tags"] == [
        "leap_second",
        "tai_utc_conversion",
        "time_scale_conversion",
    ]
    assert variables[("utc2tai", "delta_at")]["variable_role"] == "parameter"
    assert variables[("utc2tai", "delta_at")]["dim_signature"] == "T1"


def test_tempo_jl_find_year_fixture_matches_live_symbolic_manifest() -> None:
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


def test_tempo_jl_find_year_fixture_loads_without_database_io() -> None:
    fixture = _fixture()
    artifact_ids = {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-{index:012d}",
            "version_id": f"30000000-0000-0000-0000-{index:012d}",
        }
        for index, row in enumerate(
            fixture["artifact_symbolic_expressions"],
            start=1,
        )
    }
    result = load_symbolic_publication_manifest(fixture, artifact_ids)

    assert result.diagnostics == ()
    rows = result.to_insert_rows()
    assert len(rows["artifact_symbolic_expressions"]) == 15
    assert len(rows["artifact_symbolic_variables"]) == 90
    assert len(rows["artifact_validity_bounds"]) == 44
