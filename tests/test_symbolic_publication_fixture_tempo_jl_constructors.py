from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAMES = {
    "date_from_offset",
    "date_from_year_dayinyear",
    "datetime_from_seconds",
    "time_from_secondinday",
    "time_from_secondinday_fraction",
}


def _fixture(name: str) -> dict:
    path = REPO_ROOT / "data" / "publication_fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_constructor_fixture(fixture: dict, module: str) -> None:
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

    assert fixture["modules"] == [module]
    assert set(expressions) == EXPECTED_NAMES
    assert len(fixture["artifact_symbolic_expressions"]) == 5
    assert len(fixture["artifact_symbolic_variables"]) == 34
    assert len(fixture["artifact_validity_bounds"]) == 19

    date_from_offset = expressions["date_from_offset"]
    assert date_from_offset["raw_formula"] == (
        "Eq(offset, day + last_j2000_day + previous_month_day)"
    )
    assert date_from_offset["constants"] == {}
    assert "calendar_arithmetic" in date_from_offset["mechanism_tags"]
    assert variables[("date_from_offset", "offset")]["variable_role"] == "input"
    assert variables[("date_from_offset", "day")]["variable_role"] == "output"
    assert bounds[("date_from_offset", "month")]["min_value"] == 1.0

    time_from_secondinday = expressions["time_from_secondinday"]
    assert time_from_secondinday["raw_formula"] == (
        "Eq(secondinday, h*hour_seconds + m*minute_seconds + s)"
    )
    assert time_from_secondinday["constants"] == {
        "hour_seconds": 3600.0,
        "minute_seconds": 60.0,
    }
    assert "time_of_day_conversion" in time_from_secondinday["mechanism_tags"]
    assert variables[("time_from_secondinday", "s")]["variable_role"] == "output"
    assert bounds[("time_from_secondinday", "secondinday")]["max_value"] == 86400.0

    datetime_from_seconds = expressions["datetime_from_seconds"]
    assert datetime_from_seconds["raw_formula"] == (
        "Eq(julian_day, jd_epoch + seconds/day_seconds)"
    )
    assert datetime_from_seconds["constants"] == {
        "day_seconds": 86400.0,
        "jd_epoch": 2451545.0,
    }
    assert "julian_date" in datetime_from_seconds["mechanism_tags"]
    assert variables[("datetime_from_seconds", "Y")]["variable_role"] == "output"


def test_tempo_find_month_constructor_publication_fixture() -> None:
    _assert_constructor_fixture(
        _fixture("tempo_jl_find_month.publication_manifest.json"),
        "sciona.atoms.physics.tempo_jl.find_month.atoms",
    )


def test_tempo_jd2cal_constructor_publication_fixture() -> None:
    _assert_constructor_fixture(
        _fixture("tempo_jl_jd2cal.publication_manifest.json"),
        "sciona.atoms.physics.tempo_jl.jd2cal.atoms",
    )
