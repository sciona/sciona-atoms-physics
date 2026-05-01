from __future__ import annotations

import json
from pathlib import Path

from sciona.atoms.physics.symbolic_publication_manifest import (
    build_symbolic_publication_manifest,
)
from sciona.physics_ingest.pdg_cdg import build_pdg_relationship_ingest
from sciona.physics_ingest.pipeline import run_physics_publication_pipeline
from sciona.physics_ingest.review import assess_publishability
from sciona.physics_ingest.sources.pdg import parse_pdg_document


REPO_ROOT = Path(__file__).resolve().parents[1]
SKYFIELD_REVIEW_BUNDLE = (
    REPO_ROOT / "docs" / "review-bundles" / "skyfield_review_bundle.json"
)
SKYFIELD_MODULE = "sciona.atoms.physics.skyfield.atoms"


def _skyfield_manifest() -> dict:
    return build_symbolic_publication_manifest(modules=(SKYFIELD_MODULE,))


def _row_for_atom(manifest: dict, atom_name: str) -> dict:
    return next(
        row
        for row in manifest["artifact_symbolic_expressions"]
        if row["atom_name"] == atom_name
    )


def _review_bundle_row(atom_name: str) -> dict:
    bundle = json.loads(SKYFIELD_REVIEW_BUNDLE.read_text(encoding="utf-8"))
    atom_key = f"sciona.atoms.physics.skyfield.{atom_name}"
    return next(row for row in bundle["rows"] if atom_key in row["atom_keys"])


def _review_ready_expression(expression: dict, review_row: dict) -> dict:
    return {
        **expression,
        "review_status": "human_reviewed",
        "evidence_json": {
            "artifact_key": expression["artifact_key"],
            "local_artifact_key": expression["local_artifact_key"],
            "registry_name": expression["registry_name"],
            "artifact_uuid": expression["artifact_uuid"],
            "bibliography": expression["bibliography"],
            "parse_roundtrip": {"status": "passed"},
            "dimensional_analysis": {"status": "passed"},
            "human_review": {
                "reviewer_id": "sciona-atoms-physics-review-bundle",
                "reviewed_at": "2026-05-01T00:00:00Z",
                "review_record_path": review_row["review_record_path"],
                "row_id": review_row["row_id"],
            },
        },
    }


def _variables_for(manifest: dict, expression: dict) -> list[dict]:
    return [
        row
        for row in manifest["artifact_symbolic_variables"]
        if row["artifact_key"] == expression["artifact_key"]
    ]


def _bounds_for(manifest: dict, expression: dict) -> list[dict]:
    return [
        row
        for row in manifest["artifact_validity_bounds"]
        if row["artifact_key"] == expression["artifact_key"]
    ]


def _references_from_review_row(review_row: dict) -> list[dict]:
    return [
        {
            "title": source["ref_id"],
            "verified": True,
            "review_status": "human_reviewed",
            "confidence": source["confidence"],
            "notes": source["notes"],
        }
        for source in review_row["authoritative_sources"]
    ]


def _io_specs_from_variables(variables: list[dict]) -> list[dict]:
    return [
        {
            "name": row["symbol_name"],
            "direction": row["variable_role"],
            "dim_signature": row["dim_signature"],
        }
        for row in variables
    ]


def _artifact_bindings(manifest: dict) -> dict[str, dict[str, str]]:
    return {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-{index:012d}",
            "version_id": f"30000000-0000-0000-0000-{index:012d}",
        }
        for index, row in enumerate(
            manifest["artifact_symbolic_expressions"], start=1
        )
    }


def test_symbolic_manifest_fixture_satisfies_matcher_review_gates() -> None:
    manifest = _skyfield_manifest()
    expression = _row_for_atom(manifest, "calculate_vector_angle")
    review_row = _review_bundle_row("calculate_vector_angle")
    variables = _variables_for(manifest, expression)
    bounds = _bounds_for(manifest, expression)

    assessment = assess_publishability(
        candidate={
            "raw_formula": expression["raw_formula"],
            "candidate_status": "human_reviewed",
            "parse_confidence": expression["parse_confidence"],
        },
        expression=_review_ready_expression(expression, review_row),
        variables=variables,
        references=_references_from_review_row(review_row),
        validity_bounds=bounds,
        io_specs=_io_specs_from_variables(variables),
    )

    assert assessment.publishable is True
    assert assessment.achieved_status == "published"
    assert [gate.status for gate in assessment.gates] == [
        "raw_imported",
        "parsed",
        "dimension_resolved",
        "symbolically_validated",
        "source_verified",
        "human_reviewed",
        "published",
    ]
    assert all(gate.passed for gate in assessment.gates)


def test_symbolic_manifest_bindings_feed_pdg_publication_dry_run() -> None:
    manifest = _skyfield_manifest()
    rows_by_name = {
        row["atom_name"]: row for row in manifest["artifact_symbolic_expressions"]
    }
    bindings = _artifact_bindings(manifest)

    pdg_bundle = parse_pdg_document(
        {
            "equations": [
                {
                    "id": "eq:spherical_rates",
                    "label": "Skyfield spherical coordinate rates",
                    "latex": "r,lat,lon,dr,dlat,dlon",
                },
                {
                    "id": "eq:vector_angle",
                    "label": "Skyfield vector angle",
                    "latex": "cos(theta) = dot(u,w)/(norm(u) norm(w))",
                },
            ],
            "inference_edges": [
                {
                    "id": "edge:angle_component",
                    "source": "eq:spherical_rates",
                    "target": "eq:vector_angle",
                    "rule": "derive",
                    "confidence": 0.9,
                }
            ],
        }
    )

    pdg_result = build_pdg_relationship_ingest(
        pdg_bundle,
        expression_bindings_by_pdg_node_id={
            "eq:spherical_rates": {
                "expression_id": rows_by_name["compute_spherical_coordinate_rates"][
                    "expression_id"
                ],
                "artifact_id": bindings[
                    rows_by_name["compute_spherical_coordinate_rates"]["artifact_key"]
                ]["artifact_id"],
                "version_id": bindings[
                    rows_by_name["compute_spherical_coordinate_rates"]["artifact_key"]
                ]["version_id"],
                "label": "compute_spherical_coordinate_rates",
            },
            "eq:vector_angle": {
                "expression_id": rows_by_name["calculate_vector_angle"][
                    "expression_id"
                ],
                "artifact_id": bindings[
                    rows_by_name["calculate_vector_angle"]["artifact_key"]
                ]["artifact_id"],
                "version_id": bindings[
                    rows_by_name["calculate_vector_angle"]["artifact_key"]
                ]["version_id"],
                "label": "calculate_vector_angle",
            },
        },
    )
    pipeline_result = run_physics_publication_pipeline(
        publication_manifests=(manifest,),
        artifact_bindings=bindings,
        dry_run=True,
    )

    assert pdg_result.skipped_edges == ()
    assert len(pdg_result.relationship_insert_rows()) == 1
    assert pdg_result.relationship_insert_rows()[0]["source_expression_id"] == (
        rows_by_name["calculate_vector_angle"]["expression_id"]
    )
    assert pdg_result.cdg_candidate_manifests[0]["nodes"][0][
        "input_expressions"
    ][0]["artifact_id"]
    assert pipeline_result.summary.has_errors is False
    assert pipeline_result.summary.dry_run is True
    assert pipeline_result.summary.publication_manifest_count == 1
    assert pipeline_result.write_plan.ordered_tables() == (
        "artifact_symbolic_expressions",
        "artifact_symbolic_variables",
        "artifact_validity_bounds",
    )
