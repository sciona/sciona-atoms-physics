from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "docs/review-bundles/tempo_jl_review_bundle.json"
REFERENCES_PATH = REPO_ROOT / "src/sciona/atoms/physics/tempo_jl/apply_offsets/references.json"
ATOM_KEY = "sciona.atoms.physics.tempo_jl.apply_offsets._zero_offset"


class _JuliaMainStub:
    def eval(self, expression: str) -> object:
        raise RuntimeError(f"Julia FFI is unavailable in metadata tests: {expression}")


def _install_juliacall_stub() -> None:
    module = sys.modules.get("juliacall")
    if module is None or not hasattr(module, "Main"):
        sys.modules["juliacall"] = SimpleNamespace(Main=_JuliaMainStub())


def test_zero_offset_is_registered_and_reviewed() -> None:
    _install_juliacall_stub()
    module = importlib.import_module("sciona.atoms.physics.tempo_jl.apply_offsets.atoms")
    registry = importlib.import_module("sciona.ghost.registry").REGISTRY
    bundle = json.loads(BUNDLE_PATH.read_text())
    references = json.loads(REFERENCES_PATH.read_text())

    assert module._zero_offset(0.0) == 0.0
    assert module._zero_offset(42.5) == 0.0
    assert "_zero_offset" in registry

    reviewed_atom_keys = {
        atom_key
        for row in bundle["rows"]
        for atom_key in row["atom_keys"]
    }
    assert ATOM_KEY in reviewed_atom_keys

    reference_keys = references["atoms"].keys()
    assert any(key.startswith(f"{ATOM_KEY}@") for key in reference_keys)
