from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "docs/review-bundles/tempo_jl_review_bundle.json"


class _JuliaMainStub:
    def eval(self, expression: str) -> object:
        raise RuntimeError(f"Julia FFI is unavailable in metadata tests: {expression}")


def _install_juliacall_stub() -> None:
    module = sys.modules.get("juliacall")
    if module is None or not hasattr(module, "Main"):
        sys.modules["juliacall"] = SimpleNamespace(Main=_JuliaMainStub())


def test_tempo_jl_review_bundle_maps_to_registered_atoms() -> None:
    _install_juliacall_stub()
    bundle = json.loads(BUNDLE_PATH.read_text())
    registry = importlib.import_module("sciona.ghost.registry").REGISTRY

    assert bundle["family"] == "sciona.atoms.physics.tempo_jl"
    assert (REPO_ROOT / bundle["review_record_path"]).exists()

    for row in bundle["rows"]:
        importlib.import_module(row["module"])
        for atom_key in row["atom_keys"]:
            leaf = atom_key.rsplit(".", 1)[-1]
            assert leaf in registry, f"missing registry entry for {leaf} in {row['module']}"
