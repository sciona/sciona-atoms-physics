from __future__ import annotations

import json
from pathlib import Path

from sciona.atoms.physics.symbolic_publication_manifest import (
    DEFAULT_SYMBOLIC_ATOM_MODULES,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "publication_fixtures"


def test_default_symbolic_atom_modules_have_publication_fixtures() -> None:
    fixture_paths = sorted(FIXTURE_DIR.glob("*.publication_manifest.json"))
    modules_by_fixture = {
        path.name: sorted(
            json.loads(path.read_text(encoding="utf-8")).get("modules", ())
        )
        for path in fixture_paths
    }
    covered_modules = {
        module
        for fixture_modules in modules_by_fixture.values()
        for module in fixture_modules
    }
    missing_modules = set(DEFAULT_SYMBOLIC_ATOM_MODULES) - covered_modules

    assert fixture_paths, "expected checked-in publication fixture manifests"
    assert not missing_modules, (
        "default symbolic atom modules missing checked-in publication fixtures: "
        f"{sorted(missing_modules)}; fixture inventory: {modules_by_fixture}"
    )
