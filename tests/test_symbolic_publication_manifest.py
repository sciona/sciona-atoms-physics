from __future__ import annotations

from sciona.atoms.physics.symbolic_publication_manifest import (
    DEFAULT_SYMBOLIC_ATOM_MODULES,
    build_symbolic_publication_manifest,
)


def _manifest() -> dict:
    return build_symbolic_publication_manifest()


def test_manifest_contract_is_side_effect_free_publication_scaffold() -> None:
    manifest = _manifest()

    assert manifest["provider"] == "sciona-atoms-physics"
    assert manifest["modules"] == list(DEFAULT_SYMBOLIC_ATOM_MODULES)
    assert set(manifest) == {
        "provider",
        "modules",
        "artifact_symbolic_expressions",
        "artifact_symbolic_variables",
        "artifact_validity_bounds",
    }

    expression = manifest["artifact_symbolic_expressions"][0]
    assert set(expression) == {
        "artifact_key",
        "provider",
        "atom_name",
        "atom_module",
        "registry_name",
        "expression_srepr",
        "expression_text",
        "variables",
        "dim_signature",
        "symbolic_dim_signature",
        "constants",
        "bibliography",
        "local_artifact_key",
        "artifact_uuid",
    }
    assert expression["artifact_key"].startswith("local:sciona-atoms-physics:")
    assert expression["artifact_uuid"] is None
    assert isinstance(expression["variables"], dict)
    assert isinstance(expression["dim_signature"], dict)


def test_manifest_is_deterministic_and_uses_local_keys_without_uuids() -> None:
    first = _manifest()
    second = _manifest()

    assert first == second
    keys = [row["artifact_key"] for row in first["artifact_symbolic_expressions"]]
    assert len(keys) == len(set(keys))
    assert all(key.startswith("local:sciona-atoms-physics:") for key in keys)


def test_manifest_covers_migrated_symbolic_atom_packages() -> None:
    rows = {
        row["atom_name"]: row for row in _manifest()["artifact_symbolic_expressions"]
    }

    assert {
        "dm_candidate_filter",
        "circle_from_three_points",
        "helix_pitch_from_two_points",
        "helix_pitch_least_squares",
        "helix_direction_from_two_points",
        "helix_nearest_point_distance",
        "compute_spherical_coordinate_rates",
        "calculate_vector_angle",
        "_zero_offset",
        "apply_offsets",
        "offset_tt2tdb",
        "offset_tt2tdbh",
        "tt2tdb_offset",
    }.issubset(rows)

    assert rows["dm_candidate_filter"]["atom_module"].endswith("pulsar_folding.dm_can")
    assert rows["circle_from_three_points"]["atom_module"].endswith(
        "particle_tracking.helix_geometry.atoms"
    )
    assert rows["calculate_vector_angle"]["atom_module"].endswith("skyfield.atoms")
    assert rows["offset_tt2tdb"]["atom_module"].endswith("tempo_jl.offsets.atoms")


def test_manifest_emits_expression_variables_and_bounds_rows() -> None:
    manifest = _manifest()
    expression_rows = manifest["artifact_symbolic_expressions"]
    variable_rows = manifest["artifact_symbolic_variables"]
    bound_rows = manifest["artifact_validity_bounds"]

    rows_by_name = {row["atom_name"]: row for row in expression_rows}
    keys_by_name = {row["atom_name"]: row["artifact_key"] for row in expression_rows}

    dm_key = keys_by_name["dm_candidate_filter"]
    dm_variables = {
        row["symbol"]: row
        for row in variable_rows
        if row["artifact_key"] == dm_key
    }
    assert dm_variables["DM"]["role"] == "input"
    assert dm_variables["DM"]["dim_signature"] == "L-2"
    assert dm_variables["delay"]["role"] == "output"
    assert dm_variables["delay"]["dim_signature"] == "T1"
    assert rows_by_name["dm_candidate_filter"]["constants"]["K"] == 4.148808e3

    angle_key = keys_by_name["calculate_vector_angle"]
    angle_bounds = {
        row["symbol"]: row
        for row in bound_rows
        if row["artifact_key"] == angle_key
    }
    assert angle_bounds["theta"]["min_value"] == 0.0
    assert angle_bounds["theta"]["max_value"] > 3.0
    assert angle_bounds["u_norm"]["max_value"] is None

    low_order = rows_by_name["offset_tt2tdb"]
    assert low_order["constants"]["m1"] == 1.99096871e-7
    assert low_order["dim_signature"]["seconds"] == "T1"
    assert low_order["dim_signature"]["m1"] == "T-1"


def test_manifest_can_be_limited_to_selected_modules() -> None:
    manifest = build_symbolic_publication_manifest(
        modules=("sciona.atoms.physics.tempo_jl.offsets.atoms",)
    )
    names = {row["atom_name"] for row in manifest["artifact_symbolic_expressions"]}

    assert names == {"offset_tt2tdb", "offset_tt2tdbh", "tt2tdb_offset"}
    assert {
        row["atom_module"] for row in manifest["artifact_symbolic_expressions"]
    } == {"sciona.atoms.physics.tempo_jl.offsets.atoms"}
