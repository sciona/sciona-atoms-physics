from __future__ import annotations

from sciona.atoms.physics.symbolic_publication_manifest import (
    build_symbolic_publication_manifest,
)
from sciona.physics_ingest.pipeline import run_physics_publication_pipeline


def test_symbolic_manifest_runs_through_matcher_publication_pipeline_dry_run() -> None:
    manifest = build_symbolic_publication_manifest()
    expression_rows = manifest["artifact_symbolic_expressions"]
    artifact_bindings = {
        row["artifact_key"]: {
            "artifact_id": f"20000000-0000-0000-0000-{index:012d}",
            "version_id": f"30000000-0000-0000-0000-{index:012d}",
        }
        for index, row in enumerate(expression_rows, start=1)
    }

    result = run_physics_publication_pipeline(
        publication_manifests=(manifest,),
        artifact_bindings=artifact_bindings,
        dry_run=True,
    )

    assert not result.summary.has_errors
    assert result.summary.dry_run is True
    assert result.summary.publication_manifest_count == 1
    assert result.summary.source_bundle_count == 0
    assert result.summary.affected_row_count == 0
    assert result.write_result is not None
    assert result.write_result.dry_run is True
    assert result.write_result.affected_count == 0
    assert all(row["severity"] != "error" for row in result.diagnostics)

    insert_rows = result.orchestration_result.to_insert_rows()
    assert len(insert_rows["artifact_symbolic_expressions"]) == len(expression_rows)
    assert len(insert_rows["artifact_symbolic_variables"]) == len(
        manifest["artifact_symbolic_variables"]
    )
    assert len(insert_rows["artifact_validity_bounds"]) == len(
        manifest["artifact_validity_bounds"]
    )

    assert result.write_plan.ordered_tables() == (
        "artifact_symbolic_expressions",
        "artifact_symbolic_variables",
        "artifact_validity_bounds",
    )
    assert result.summary.planned_row_count == sum(
        len(rows) for rows in insert_rows.values()
    )
    assert {
        diagnostic["reason"] for diagnostic in result.diagnostics
    } == {"dry_run"}
