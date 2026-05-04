from __future__ import annotations

from sciona.atoms.physics.symbolic_publication_manifest import (
    DEFAULT_SYMBOLIC_ATOM_MODULES,
    build_symbolic_publication_manifest,
    to_matcher_symbolic_expression_rows,
)
from sciona.physics_ingest.publication import load_symbolic_publication_manifest
from sciona.physics_ingest.staging import validate_symbolic_expression_row


ARTIFACT_ID = "20000000-0000-0000-0000-000000000001"
VERSION_ID = "30000000-0000-0000-0000-000000000001"


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
    assert set(expression).issuperset(
        {
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
    )
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

    source_ids = [
        row["source_expression_id"] for row in first["artifact_symbolic_expressions"]
    ]
    expression_ids = [
        row["expression_id"] for row in first["artifact_symbolic_expressions"]
    ]
    assert len(source_ids) == len(set(source_ids))
    assert len(expression_ids) == len(set(expression_ids))
    assert all(
        source_id.startswith("sciona-atoms-physics:") for source_id in source_ids
    )


def test_manifest_covers_migrated_symbolic_atom_packages() -> None:
    rows = {
        row["atom_name"]: row for row in _manifest()["artifact_symbolic_expressions"]
    }

    assert {
        "SNR",
        "bayesian_neighbor_evaluation",
        "coordinate_rescaling_for_knn",
        "de_disperse",
        "dedispersionkernel",
        "delay_from_DM",
        "dm_can_brute_force",
        "dm_candidate_filter",
        "fold_signal",
        "greedy_track_commit",
        "helix_cap_intersection",
        "helix_cylinder_intersection",
        "perturbative_cap_correction",
        "perturbative_cylinder_correction",
        "spline_bandpass_correction",
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
        "tai_to_utc_inversion",
        "utc_to_tai_leap_second_kernel",
    }.issubset(rows)

    assert rows["dedispersionkernel"]["atom_module"].endswith("astroflow.atoms")
    assert rows["delay_from_DM"]["atom_module"].endswith("pulsar.pipeline")
    assert rows["dm_can_brute_force"]["atom_module"].endswith("pulsar_folding.atoms")
    assert rows["dm_candidate_filter"]["atom_module"].endswith("pulsar_folding.dm_can")
    assert rows["coordinate_rescaling_for_knn"]["atom_module"].endswith(
        "detector_corrections.atoms"
    )
    assert rows["helix_cylinder_intersection"]["atom_module"].endswith(
        "track_matching.atoms"
    )
    assert rows["circle_from_three_points"]["atom_module"].endswith(
        "particle_tracking.helix_geometry.atoms"
    )
    assert rows["calculate_vector_angle"]["atom_module"].endswith("skyfield.atoms")
    assert rows["offset_tt2tdb"]["atom_module"].endswith("tempo_jl.offsets.atoms")
    assert rows["tai_to_utc_inversion"]["atom_module"].endswith(
        "tempo_jl.tai2utc_d12.atoms"
    )


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
    assert dm_variables["DM"]["variable_role"] == "input"
    assert dm_variables["DM"]["symbol_name"] == "DM"
    assert dm_variables["DM"]["source_symbol"] == "DM"
    assert dm_variables["DM"]["dim_signature"] == "L-2"
    assert dm_variables["DM"]["dimension_source"] == "source"
    assert dm_variables["DM"]["ordinal"] < dm_variables["delay"]["ordinal"]
    assert dm_variables["DM"]["source_variable_id"].endswith(
        ":dm_candidate_filter:variable:DM"
    )
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
    assert angle_bounds["theta"]["lower_value"] == 0.0
    assert angle_bounds["theta"]["max_value"] > 3.0
    assert angle_bounds["theta"]["upper_value"] > 3.0
    assert angle_bounds["theta"]["variable_name"] == "theta"
    assert angle_bounds["theta"]["source_symbol"] == "theta"
    assert angle_bounds["theta"]["scope"] == "variable"
    assert angle_bounds["theta"]["bound_kind"] == "domain"
    assert angle_bounds["theta"]["confidence"] == "high"
    assert angle_bounds["theta"]["review_status"] == "automated_pass"
    assert angle_bounds["theta"]["validity_statement"].startswith("0.0 <= theta <=")
    assert angle_bounds["theta"]["source_bound_id"].endswith(
        ":calculate_vector_angle:bound:theta"
    )
    assert angle_bounds["theta"]["evidence_ref_key"] == angle_bounds["theta"][
        "source_bound_id"
    ]
    assert angle_bounds["theta"]["metadata"]["source_symbol"] == "theta"
    assert angle_bounds["u_norm"]["max_value"] is None
    assert angle_bounds["u_norm"]["validity_statement"] == "u_norm >= 0.0"

    low_order = rows_by_name["offset_tt2tdb"]
    assert low_order["constants"]["m1"] == 1.99096871e-7
    assert low_order["dim_signature"]["seconds"] == "T1"
    assert low_order["dim_signature"]["m1"] == "T-1"


def test_manifest_emits_stable_hashes_tags_and_loader_fields() -> None:
    rows = {
        row["atom_name"]: row for row in _manifest()["artifact_symbolic_expressions"]
    }
    dm = rows["dm_candidate_filter"]
    dedispersion = rows["dedispersionkernel"]
    pulsar_delay = rows["delay_from_DM"]
    pulsar_fold = rows["fold_signal"]
    pulsar_snr = rows["SNR"]
    folding_search = rows["dm_can_brute_force"]
    bandpass = rows["spline_bandpass_correction"]
    detector_rescale = rows["coordinate_rescaling_for_knn"]
    detector_cap = rows["perturbative_cap_correction"]
    detector_cylinder = rows["perturbative_cylinder_correction"]
    matching_cylinder = rows["helix_cylinder_intersection"]
    matching_bayes = rows["bayesian_neighbor_evaluation"]
    matching_greedy = rows["greedy_track_commit"]
    helix = rows["helix_pitch_least_squares"]
    angle = rows["calculate_vector_angle"]
    low_order = rows["offset_tt2tdb"]
    leap_forward = rows["utc_to_tai_leap_second_kernel"]

    for row in rows.values():
        assert len(row["canonical_expr_hash"]) == 64
        assert len(row["topology_hash"]) == 64
        assert len(row["dimensional_hash"]) == 64
        assert row["sympy_srepr"] == row["expression_srepr"]
        assert row["raw_formula"] == row["expression_text"]
        assert row["raw_formula_format"] == "plain_text"
        assert row["expression_kind"] == "equation"
        assert row["expression_role"] == "primary"
        assert row["parse_status"] == "normalized"
        assert row["parse_confidence"] == 1.0
        assert row["review_status"] == "automated_pass"
        assert row["validation_status"] == "passed"
        assert row["source_expression_id"].endswith(
            f":{row['atom_module']}:{row['atom_name']}"
        )

    assert dm["mechanism_tags"] == [
        "dispersion",
        "pulsar_search",
        "signal_processing",
    ]
    assert dm["behavioral_archetypes"] == ["candidate_scoring", "delay_model"]
    assert dedispersion["mechanism_tags"] == [
        "dedispersion",
        "pulsar_search",
        "signal_processing",
    ]
    assert dedispersion["behavioral_archetypes"] == [
        "channel_aggregation",
        "delay_alignment",
    ]
    assert pulsar_delay["mechanism_tags"] == [
        "dispersion_measure",
        "pulsar_timing",
        "signal_propagation",
    ]
    assert pulsar_delay["behavioral_archetypes"] == [
        "delay_model",
        "inverse_square_scaling",
    ]
    assert pulsar_fold["behavioral_archetypes"] == [
        "phase_folding",
        "windowed_average",
    ]
    assert pulsar_snr["behavioral_archetypes"] == ["log_ratio", "peak_to_background"]
    assert folding_search["mechanism_tags"] == [
        "pulsar_search",
        "shift_search",
        "signal_processing",
    ]
    assert folding_search["behavioral_archetypes"] == [
        "argmax_selection",
        "snr_scoring",
    ]
    assert bandpass["mechanism_tags"] == [
        "bandpass_correction",
        "instrumental_baseline",
        "signal_processing",
    ]
    assert bandpass["behavioral_archetypes"] == [
        "baseline_subtraction",
        "spline_smoothing",
    ]
    assert detector_rescale["behavioral_archetypes"] == [
        "coordinate_rescaling",
        "radius_normalization",
    ]
    assert detector_cap["behavioral_archetypes"] == [
        "azimuthal_radial_correction",
        "perturbative_update",
    ]
    assert detector_cylinder["behavioral_archetypes"] == [
        "curvature_scaled_update",
        "perturbative_update",
    ]
    assert matching_cylinder["behavioral_archetypes"] == [
        "cylinder_intersection",
        "phase_advance",
    ]
    assert matching_bayes["behavioral_archetypes"] == [
        "likelihood_ratio_cut",
        "normalized_distance",
    ]
    assert matching_greedy["behavioral_archetypes"] == [
        "greedy_selection",
        "loss_fraction_gate",
    ]
    assert "particle_tracking" in helix["mechanism_tags"]
    assert "least_squares_fit" in helix["behavioral_archetypes"]
    assert "coordinate_transform" in angle["mechanism_tags"]
    assert "time_scale_conversion" in low_order["mechanism_tags"]
    assert leap_forward["mechanism_tags"] == [
        "leap_second",
        "tai_utc_conversion",
        "time_scale_conversion",
    ]
    assert leap_forward["behavioral_archetypes"] == [
        "inverse_time_mapping",
        "leap_offset",
    ]


def test_manifest_rows_can_be_adapted_to_matcher_staging_contract() -> None:
    expression_rows = _manifest()["artifact_symbolic_expressions"]
    artifact_id_by_key = {row["artifact_key"]: ARTIFACT_ID for row in expression_rows}
    version_id_by_key = {row["artifact_key"]: VERSION_ID for row in expression_rows}

    loader_rows = to_matcher_symbolic_expression_rows(
        expression_rows,
        artifact_id_by_key=artifact_id_by_key,
        version_id_by_key=version_id_by_key,
    )

    assert len(loader_rows) == len(expression_rows)
    staged = [validate_symbolic_expression_row(row) for row in loader_rows]
    assert {row.expression_id for row in staged} == {
        row["expression_id"] for row in expression_rows
    }
    assert all(row.artifact_id == ARTIFACT_ID for row in staged)
    assert all(row.version_id == VERSION_ID for row in staged)
    assert staged[0].to_insert_dict()["source_expression_id"]


def test_manifest_rows_load_through_matcher_publication_loader_with_bindings() -> None:
    manifest = _manifest()
    expression_rows = manifest["artifact_symbolic_expressions"]
    artifact_bindings = {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-{index:012d}",
            "version_id": f"30000000-0000-0000-0000-{index:012d}",
        }
        for index, row in enumerate(expression_rows, start=1)
    }

    result = load_symbolic_publication_manifest(manifest, artifact_bindings)
    rows = result.to_insert_rows()

    assert result.diagnostics == ()
    assert len(rows["artifact_symbolic_expressions"]) == len(expression_rows)
    assert len(rows["artifact_symbolic_variables"]) == len(
        manifest["artifact_symbolic_variables"]
    )
    assert len(rows["artifact_validity_bounds"]) == len(
        manifest["artifact_validity_bounds"]
    )

    variable = next(
        row
        for row in rows["artifact_symbolic_variables"]
        if (
            row["evidence_json"]["publication_manifest"]["atom_name"]
            == "dm_candidate_filter"
            and row["symbol_name"] == "DM"
        )
    )
    assert variable["source_symbol"] == "DM"
    assert variable["dimension_source"] == "source"
    assert variable["ordinal"] >= 0

    bound = next(
        row
        for row in rows["artifact_validity_bounds"]
        if (
            row["metadata"]["publication_manifest"]["atom_name"]
            == "dm_candidate_filter"
            and row["variable_name"] == "DM"
        )
    )
    assert bound["scope"] == "variable"
    assert bound["confidence"] == "high"
    assert bound["metadata"]["publication_manifest"]["source_bound_id"].endswith(
        ":dm_candidate_filter:bound:DM"
    )


def test_manifest_can_be_limited_to_selected_modules() -> None:
    manifest = build_symbolic_publication_manifest(
        modules=("sciona.atoms.physics.tempo_jl.offsets.atoms",)
    )
    names = {row["atom_name"] for row in manifest["artifact_symbolic_expressions"]}

    assert names == {"offset_tt2tdb", "offset_tt2tdbh", "tt2tdb_offset"}
    assert {
        row["atom_module"] for row in manifest["artifact_symbolic_expressions"]
    } == {"sciona.atoms.physics.tempo_jl.offsets.atoms"}
