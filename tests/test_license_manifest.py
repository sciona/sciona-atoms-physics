from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "licenses" / "provider_license.json"
EXPECTED_UNRESOLVED = {
    "sciona.atoms.physics.astroflow",
    "sciona.atoms.physics.jFOF",
    "sciona.atoms.physics.pasqal",
    "sciona.atoms.physics.pulsar",
    "sciona.atoms.physics.pulsar_folding",
    "sciona.atoms.physics.skyfield",
    "sciona.atoms.physics.tempo_jl",
}


def test_physics_license_manifest_defaults_to_unknown() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())

    assert manifest["provider_repo"] == "sciona-atoms-physics"
    assert manifest["repo_default_license"]["license_spdx"] == "NOASSERTION"
    assert manifest["repo_default_license"]["status"] == "unknown"
    assert manifest["family_overrides"] == []

    unresolved = {row["family"] for row in manifest["unresolved_families"]}
    assert unresolved == EXPECTED_UNRESOLVED
