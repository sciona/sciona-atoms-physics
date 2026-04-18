from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_PATH = REPO_ROOT / "src/sciona/atoms/physics/pulsar_folding/references.json"


def test_pulsar_folding_nested_dm_can_reference_key_is_canonical() -> None:
    payload = json.loads(REFERENCES_PATH.read_text())
    atoms = payload["atoms"]

    assert "sciona.atoms.physics.pulsar_folding.dm_can.dm_candidate_filter@sciona/atoms/physics/pulsar_folding/dm_can.py:16" in atoms
    assert "sciona.atoms.physics.pulsar_folding.dm_candidate_filter@sciona/atoms/physics/pulsar_folding/dm_can.py:16" not in atoms
