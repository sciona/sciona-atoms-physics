from __future__ import annotations

import importlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "docs/review-bundles/pasqal_docking_review_bundle.json"


def test_pasqal_review_bundle_maps_to_registered_atoms() -> None:
    bundle = json.loads(BUNDLE_PATH.read_text())
    registry = importlib.import_module("sciona.ghost.registry").REGISTRY

    assert bundle["family"] == "sciona.atoms.physics.pasqal.docking"
    assert (REPO_ROOT / bundle["review_record_path"]).exists()

    reviewed_atom_keys = set()
    for row in bundle["rows"]:
        importlib.import_module(row["module"])
        for atom_key in row["atom_keys"]:
            reviewed_atom_keys.add(atom_key)
            leaf = atom_key.rsplit(".", 1)[-1]
            assert leaf in registry, f"missing registry entry for {leaf} in {row['module']}"

    assert reviewed_atom_keys == {
        "sciona.atoms.physics.pasqal.docking.graph_transformer",
        "sciona.atoms.physics.pasqal.docking.quantum_mwis_solver",
        "sciona.atoms.physics.pasqal.docking.sub_graph_embedder",
    }
