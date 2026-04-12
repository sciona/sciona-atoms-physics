from __future__ import annotations

import importlib
import os


def test_physics_import_smoke() -> None:
    os.environ.setdefault("PYTHON_JULIACALL_INIT", "no")
    assert importlib.import_module("sciona.atoms.physics.tempo_jl") is not None
    assert importlib.import_module("sciona.probes.physics.tempo_jl") is not None
