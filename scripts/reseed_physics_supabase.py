#!/usr/bin/env python
"""Replay curated physics ingestion seed artifacts into Supabase."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "physics_ingestion_seeds" / "manifest.json"


class ReseedError(RuntimeError):
    """Raised when a seed artifact cannot be safely replayed."""


class SupabaseRestClient:
    """Small PostgREST client for deterministic write-plan replay."""

    def __init__(self, *, supabase_url: str, service_role_key: str, timeout: int = 60) -> None:
        self.supabase_url = supabase_url.rstrip("/")
        self.service_role_key = service_role_key
        self.timeout = timeout

    def upsert_rows(
        self,
        *,
        table: str,
        rows: Iterable[Mapping[str, Any]],
        conflict_keys: Iterable[str],
    ) -> int:
        rows_list = [dict(row) for row in rows]
        if not rows_list:
            return 0
        conflict_key_list = [str(key) for key in conflict_keys if str(key)]
        query = ""
        if conflict_key_list:
            query = "?" + urlencode({"on_conflict": ",".join(conflict_key_list)}, safe=",")
        url = f"{self.supabase_url}/rest/v1/{quote(table, safe='')}{query}"
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": (
                "resolution=merge-duplicates,return=minimal"
                if conflict_key_list
                else "return=minimal"
            ),
        }
        request = Request(
            url,
            data=json.dumps(rows_list, separators=(",", ":")).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout):
                return len(rows_list)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ReseedError(f"{table} upsert failed with HTTP {exc.code}: {body}") from exc
        except URLError as exc:
            raise ReseedError(f"{table} upsert failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reseed Supabase from committed sciona-atoms-physics seed artifacts."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Physics ingestion seed manifest to replay.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help="Seed id to replay. May be supplied multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify artifacts and print planned writes without calling Supabase.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List manifest seed ids and exit.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Maximum rows per PostgREST request.",
    )
    parser.add_argument(
        "--supabase-url",
        default="",
        help="Supabase URL. Defaults to SUPABASE_URL or SCIONA_SUPABASE_URL.",
    )
    parser.add_argument(
        "--service-role-key",
        default="",
        help=(
            "Supabase service role key. Defaults to SUPABASE_SERVICE_ROLE_KEY, "
            "SUPABASE_SERVICE_KEY, SCIONA_SUPABASE_SERVICE_ROLE_KEY, or "
            "SCIONA_SUPABASE_SERVICE_KEY."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP timeout in seconds for each Supabase request.",
    )
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = _load_json(manifest_path)
    seed_root = manifest_path.parent
    seeds = _select_seeds(manifest, only=args.only)
    if args.list:
        for seed in seeds:
            print(f"{seed['order']}\t{seed['seed_id']}\t{seed['total_row_count']}")
        return 0

    if args.batch_size < 1:
        raise ReseedError("--batch-size must be at least 1")

    client = None
    if not args.dry_run:
        supabase_url = args.supabase_url or _env_first("SUPABASE_URL", "SCIONA_SUPABASE_URL")
        service_role_key = args.service_role_key or _env_first(
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_SERVICE_KEY",
            "SCIONA_SUPABASE_SERVICE_ROLE_KEY",
            "SCIONA_SUPABASE_SERVICE_KEY",
        )
        if not supabase_url:
            raise ReseedError("missing Supabase URL; set SUPABASE_URL or pass --supabase-url")
        if not service_role_key:
            raise ReseedError(
                "missing Supabase service key; set SUPABASE_SERVICE_ROLE_KEY "
                "or pass --service-role-key"
            )
        client = SupabaseRestClient(
            supabase_url=supabase_url,
            service_role_key=service_role_key,
            timeout=max(args.timeout, 1),
        )

    reports = [
        replay_seed(
            seed,
            seed_root=seed_root,
            client=client,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )
        for seed in seeds
    ]
    summary = {
        "ok": True,
        "dry_run": bool(args.dry_run),
        "seed_count": len(reports),
        "total_rows": sum(int(report["total_rows"]) for report in reports),
        "seeds": reports,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def replay_seed(
    seed: Mapping[str, Any],
    *,
    seed_root: Path,
    client: SupabaseRestClient | None,
    batch_size: int,
    dry_run: bool,
) -> dict[str, Any]:
    write_plan_path = seed_root / str(seed["write_plan_path"])
    _verify_sha256(write_plan_path, str(seed["write_plan_sha256"]))
    summary_path = seed_root / str(seed["summary_path"])
    _verify_sha256(summary_path, str(seed["summary_sha256"]))
    write_plan = _load_json(write_plan_path)
    batches = list(write_plan.get("batches") or [])
    if not batches:
        raise ReseedError(f"{seed['seed_id']} has no write-plan batches")

    table_reports = []
    for batch in batches:
        table = _required_text(batch, "table")
        rows = [dict(row) for row in batch.get("rows") or []]
        conflict_keys = [str(key) for key in batch.get("conflict_keys") or []]
        applied = 0
        chunk_count = 0
        for chunk in _chunks(rows, batch_size):
            chunk_count += 1
            if dry_run:
                applied += len(chunk)
            else:
                if client is None:
                    raise ReseedError("client is required when dry_run is false")
                applied += client.upsert_rows(
                    table=table,
                    rows=chunk,
                    conflict_keys=conflict_keys,
                )
        table_reports.append(
            {
                "table": table,
                "row_count": len(rows),
                "applied_row_count": applied,
                "chunk_count": chunk_count,
                "conflict_keys": conflict_keys,
            }
        )

    return {
        "seed_id": str(seed["seed_id"]),
        "source_version": str(seed.get("source_version") or ""),
        "snapshot_id": str(seed.get("snapshot_id") or ""),
        "total_rows": sum(int(report["applied_row_count"]) for report in table_reports),
        "tables": table_reports,
    }


def _select_seeds(
    manifest: Mapping[str, Any],
    *,
    only: Iterable[str] | None,
) -> list[Mapping[str, Any]]:
    seeds = [seed for seed in manifest.get("seeds", []) if isinstance(seed, Mapping)]
    by_id = {str(seed.get("seed_id")): seed for seed in seeds}
    if only:
        selected = []
        for seed_id in only:
            if seed_id not in by_id:
                raise ReseedError(f"unknown seed id: {seed_id}")
            selected.append(by_id[seed_id])
        return sorted(selected, key=lambda seed: int(seed.get("order") or 0))
    return sorted(seeds, key=lambda seed: int(seed.get("order") or 0))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise ReseedError(f"missing seed artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReseedError(f"invalid JSON artifact {path}: {exc}") from exc


def _verify_sha256(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ReseedError(f"checksum mismatch for {path}: expected {expected}, got {actual}")


def _chunks(rows: list[Mapping[str, Any]], size: int) -> Iterable[list[Mapping[str, Any]]]:
    for offset in range(0, len(rows), size):
        yield rows[offset : offset + size]


def _required_text(row: Mapping[str, Any], key: str) -> str:
    value = str(row.get(key) or "")
    if not value:
        raise ReseedError(f"write-plan batch is missing {key}")
    return value


def _env_first(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReseedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
