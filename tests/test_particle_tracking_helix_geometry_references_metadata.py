from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS_PATH = ROOT / "src" / "sciona" / "atoms" / "particle_tracking" / "helix_geometry" / "references.json"
REGISTRY_PATH = ROOT / "data" / "references" / "registry.json"

EXPECTED_LEAF_NAMES = {
    "circle_from_three_points",
    "helix_pitch_from_two_points",
    "helix_pitch_least_squares",
    "helix_direction_from_two_points",
    "helix_nearest_point_distance",
}


def test_references_file_exists() -> None:
    assert REFS_PATH.exists()


def test_registry_file_exists() -> None:
    assert REGISTRY_PATH.exists(), "Physics repo needs its own data/references/registry.json"


def test_references_has_all_five_atoms() -> None:
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    assert refs["schema_version"] == "1.1"
    leaf_names = {k.split("@")[0].rsplit(".", 1)[-1] for k in refs["atoms"]}
    assert leaf_names == EXPECTED_LEAF_NAMES


def test_each_atom_has_nonempty_references() -> None:
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    for key, entry in refs["atoms"].items():
        assert len(entry["references"]) > 0, f"{key} has no references"


def test_ref_ids_exist_in_local_registry() -> None:
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_ids = set(registry["references"].keys())
    for key, entry in refs["atoms"].items():
        for ref in entry["references"]:
            assert ref["ref_id"] in registry_ids, (
                f"{key}: ref_id '{ref['ref_id']}' not in local registry"
            )


def test_match_metadata_fields() -> None:
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    for key, entry in refs["atoms"].items():
        for ref in entry["references"]:
            md = ref["match_metadata"]
            assert "match_type" in md
            assert "confidence" in md
            assert md.get("notes")
