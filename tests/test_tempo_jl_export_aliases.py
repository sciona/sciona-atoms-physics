from __future__ import annotations

import importlib


FAMILIES = {
    "sciona.atoms.physics.tempo_jl.find_month": {
        "date_from_offset",
        "date_from_year_dayinyear",
        "show_date",
        "time_from_hms",
        "time_from_secondinday_fraction",
        "time_from_secondinday",
        "show_time",
        "datetime_from_components",
        "datetime_from_string",
        "datetime_from_seconds",
    },
    "sciona.atoms.physics.tempo_jl.jd2cal": {
        "date_from_offset",
        "date_from_year_dayinyear",
        "show_date",
        "time_from_hms",
        "time_from_secondinday_fraction",
        "time_from_secondinday",
        "show_time",
        "datetime_from_components",
        "datetime_from_string",
        "datetime_from_seconds",
    },
}


def test_tempo_jl_packages_export_reviewed_leaf_names() -> None:
    for module_name, expected_names in FAMILIES.items():
        module = importlib.import_module(module_name)
        for name in expected_names:
            exported = getattr(module, name)
            assert callable(exported), f"{module_name}.{name} is not callable"
