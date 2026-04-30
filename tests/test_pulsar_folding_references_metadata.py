from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_PATH = REPO_ROOT / "src/sciona/atoms/physics/pulsar_folding/references.json"


def test_pulsar_folding_nested_dm_can_reference_key_is_canonical() -> None:
    payload = json.loads(REFERENCES_PATH.read_text())
    atoms = payload["atoms"]

    expected_keys = {
        "sciona.atoms.physics.pulsar_folding.dm_can_brute_force@sciona/atoms/physics/pulsar_folding/atoms.py:19",
        "sciona.atoms.physics.pulsar_folding.spline_bandpass_correction@sciona/atoms/physics/pulsar_folding/atoms.py:49",
        "sciona.atoms.physics.pulsar_folding.dm_can.dm_candidate_filter@sciona/atoms/physics/pulsar_folding/dm_can.py:34",
    }

    assert set(atoms) == expected_keys
