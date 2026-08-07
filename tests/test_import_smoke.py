from __future__ import annotations

import importlib
import os
import subprocess
import sys


def test_physics_import_smoke() -> None:
    os.environ.setdefault("PYTHON_JULIACALL_INIT", "no")
    assert importlib.import_module("sciona.atoms.physics.tempo_jl") is not None
    assert importlib.import_module("sciona.probes.physics.tempo_jl") is not None


def test_tempo_package_discovery_does_not_start_julia() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "import sciona.atoms.physics.tempo_jl; "
                "assert 'juliacall' not in sys.modules"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
