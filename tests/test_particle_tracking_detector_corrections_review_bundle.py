from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CDG_PATH = ROOT / "src" / "sciona" / "atoms" / "particle_tracking" / "detector_corrections" / "cdg.json"
REFS_PATH = ROOT / "src" / "sciona" / "atoms" / "particle_tracking" / "detector_corrections" / "references.json"
REVIEW_PATH = ROOT / "data" / "review_bundles" / "detector_corrections" / "review.json"
REGISTRY_PATH = ROOT / "data" / "references" / "registry.json"

EXPECTED_ATOM_NAMES = {
    "coordinate_rescaling_for_knn",
    "perturbative_cap_correction",
    "perturbative_cylinder_correction",
}


def test_cdg_json_exists_and_parses() -> None:
    assert CDG_PATH.exists()
    cdg = json.loads(CDG_PATH.read_text(encoding="utf-8"))
    assert "nodes" in cdg
    assert "edges" in cdg
    assert "metadata" in cdg


def test_cdg_node_ids_match_function_names() -> None:
    cdg = json.loads(CDG_PATH.read_text(encoding="utf-8"))
    atomic_names = {
        node["name"]
        for node in cdg["nodes"]
        if node.get("status") == "atomic"
    }
    assert atomic_names == EXPECTED_ATOM_NAMES


def test_cdg_node_names_are_lowercase_no_spaces() -> None:
    cdg = json.loads(CDG_PATH.read_text(encoding="utf-8"))
    for node in cdg["nodes"]:
        if node.get("status") == "atomic":
            name = node["name"]
            assert " " not in name, f"spaces in CDG name: '{name}'"
            assert name == name.lower(), f"uppercase in CDG name: '{name}'"


def test_references_json_exists_and_has_all_atoms() -> None:
    assert REFS_PATH.exists()
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    assert refs["schema_version"] == "1.1"
    leaf_names = {k.split("@")[0].rsplit(".", 1)[-1] for k in refs["atoms"]}
    assert leaf_names == EXPECTED_ATOM_NAMES


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


def test_review_json_exists_and_has_atom_names() -> None:
    assert REVIEW_PATH.exists()
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    assert "atoms" in review
    atom_names = {a["name"] for a in review["atoms"]}
    assert atom_names == EXPECTED_ATOM_NAMES
