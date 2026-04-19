from __future__ import annotations

import importlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "docs/review-bundles/pulsar_folding_review_bundle.json"
EXPECTED_ROWS = {
    "pulsar_folding/dm_can/dm_candidate_filter": {
        "module": "sciona.atoms.physics.pulsar_folding.dm_can",
        "atom_keys": {"sciona.atoms.physics.pulsar_folding.dm_can.dm_candidate_filter"},
    },
    "pulsar_folding/dm_can_brute_force": {
        "module": "sciona.atoms.physics.pulsar_folding.atoms",
        "atom_keys": {"sciona.atoms.physics.pulsar_folding.dm_can_brute_force"},
    },
    "pulsar_folding/spline_bandpass_correction": {
        "module": "sciona.atoms.physics.pulsar_folding.atoms",
        "atom_keys": {"sciona.atoms.physics.pulsar_folding.spline_bandpass_correction"},
    },
}


def test_pulsar_folding_review_bundle_maps_to_registered_atoms() -> None:
    bundle = json.loads(BUNDLE_PATH.read_text())
    registry = importlib.import_module("sciona.ghost.registry").REGISTRY

    assert bundle["family"] == "sciona.atoms.physics.pulsar_folding"
    assert (REPO_ROOT / bundle["review_record_path"]).exists()
    assert bundle["covered_rows"] == len(EXPECTED_ROWS)
    assert bundle["ready_rows"] == len(EXPECTED_ROWS)
    assert len(bundle["rows"]) == len(EXPECTED_ROWS)

    seen_row_ids = set()
    seen_atom_keys = set()
    for row in bundle["rows"]:
        expected = EXPECTED_ROWS[row["row_id"]]
        seen_row_ids.add(row["row_id"])
        seen_atom_keys.update(row["atom_keys"])

        assert row["module"] == expected["module"]
        assert set(row["atom_keys"]) == expected["atom_keys"]

        importlib.import_module(row["module"])
        for atom_key in row["atom_keys"]:
            leaf = atom_key.rsplit(".", 1)[-1]
            assert leaf in registry, f"missing registry entry for {leaf} in {row['module']}"

    assert seen_row_ids == set(EXPECTED_ROWS)
    assert seen_atom_keys == {
        atom_key
        for row in EXPECTED_ROWS.values()
        for atom_key in row["atom_keys"]
    }
