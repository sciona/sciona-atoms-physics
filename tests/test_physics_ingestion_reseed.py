from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESEED_SCRIPT = REPO_ROOT / "scripts" / "reseed_physics_supabase.py"
SEED_MANIFEST = REPO_ROOT / "data" / "physics_ingestion_seeds" / "manifest.json"

spec = importlib.util.spec_from_file_location("reseed_physics_supabase", RESEED_SCRIPT)
assert spec is not None
reseed = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reseed)


def test_seed_manifest_replays_in_declared_order_and_checksums() -> None:
    manifest = reseed._load_json(SEED_MANIFEST)
    seeds = reseed._select_seeds(manifest, only=None)

    assert [seed["seed_id"] for seed in seeds] == [
        "wikidata_physics_20260505",
        "pdg_fixture_wave1_20260505",
        "pdg_remote_wave1_20260505",
        "pdg_remote_wave2_20260505",
        "pdg_remote_wave3_20260505",
        "pdg_remote_wave4_20260505",
        "pdg_remote_wave5_20260505",
        "pdg_remote_wave6_20260505",
        "pdg_remote_wave7_20260505",
        "pdg_remote_wave8_20260505",
        "pdg_remote_wave9_20260505",
    ]
    assert manifest["total_row_count"] == sum(seed["total_row_count"] for seed in seeds)
    for seed in seeds:
        seed_root = SEED_MANIFEST.parent
        reseed._verify_sha256(seed_root / seed["write_plan_path"], seed["write_plan_sha256"])
        reseed._verify_sha256(seed_root / seed["summary_path"], seed["summary_sha256"])


def test_replay_seed_dry_run_counts_rows_without_supabase() -> None:
    manifest = reseed._load_json(SEED_MANIFEST)
    seed = reseed._select_seeds(manifest, only=["pdg_fixture_wave1_20260505"])[0]

    report = reseed.replay_seed(
        seed,
        seed_root=SEED_MANIFEST.parent,
        client=None,
        batch_size=2,
        dry_run=True,
    )

    assert report["seed_id"] == "pdg_fixture_wave1_20260505"
    assert report["total_rows"] == seed["total_row_count"]
    assert {row["table"] for row in report["tables"]}.issuperset(
        {"physics_ingest_snapshots", "artifact_symbolic_expressions"}
    )
    assert max(row["chunk_count"] for row in report["tables"]) > 1


def test_supabase_client_uses_postgrest_upsert_conflict_keys(monkeypatch) -> None:
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
            return False

    def fake_urlopen(request, timeout):  # noqa: ANN001
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return Response()

    monkeypatch.setattr(reseed, "urlopen", fake_urlopen)
    client = reseed.SupabaseRestClient(
        supabase_url="http://127.0.0.1:54321/",
        service_role_key="service-key",
        timeout=7,
    )

    count = client.upsert_rows(
        table="artifact_cdg_nodes",
        rows=[{"version_id": "v1", "node_id": "n1"}],
        conflict_keys=["version_id", "node_id"],
    )

    assert count == 1
    assert captured["url"].endswith(
        "/rest/v1/artifact_cdg_nodes?on_conflict=version_id,node_id"
    )
    assert captured["timeout"] == 7
    assert captured["headers"]["Prefer"] == "resolution=merge-duplicates,return=minimal"
    assert captured["body"] == [{"version_id": "v1", "node_id": "n1"}]
