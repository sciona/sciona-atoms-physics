from __future__ import annotations

import importlib
import json
from pathlib import Path

from sciona.atoms.physics.astroflow.witnesses import witness_dedispersionkernel
from sciona.ghost.abstract import AbstractArray, AbstractSignal


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "docs" / "review-bundles" / "astroflow_review_bundle.json"


def test_astroflow_review_bundle_maps_to_registered_atoms() -> None:
    bundle = json.loads(BUNDLE_PATH.read_text())
    registry = importlib.import_module("sciona.ghost.registry").REGISTRY

    assert bundle["family"] == "sciona.atoms.physics.astroflow"
    assert (REPO_ROOT / bundle["review_record_path"]).exists()

    for row in bundle["rows"]:
        importlib.import_module(row["module"])
        for atom_key in row["atom_keys"]:
            leaf = atom_key.rsplit(".", 1)[-1]
            assert leaf in registry, f"missing registry entry for {leaf} in {row['module']}"


def test_astroflow_witness_reports_dedispersion_shape() -> None:
    result = witness_dedispersionkernel(
        input_data=AbstractSignal(shape=(256,), dtype="float64", sampling_rate=128.0, domain="time"),
        delay_table=AbstractArray(shape=(8, 256), dtype="int64"),
        dm_steps=4,
        time_downsample=2,
        down_ndata=32,
        nchans=8,
        shared_mem_size=1024,
        block_dim_x=16,
    )

    assert result.shape == (4, 32)
    assert result.dtype == "float64"
    assert result.domain == "time"
    assert result.sampling_rate == 64.0
