# Physics Ingestion Runbook

This file captures the current operational path for ingesting external physics
equation sources into the symbolic ingestion tables.

The canonical copy of this runbook now lives in `sciona-atoms-physics` because
that repo owns the curated physics seed artifacts, the reseed script, and the
source ingestion/write-plan generation entrypoints used for future physics
waves.

## Local Supabase

Run ingestion against the Sciona Supabase stack from `../sciona-infra`.

```bash
cd ../sciona-infra
SUPABASE_GITHUB_CLIENT_ID=dummy SUPABASE_GITHUB_CLIENT_SECRET=dummy supabase start
supabase db reset --local --yes
```

Set the local PostgREST credentials in the matcher shell. Use the service role
key printed by `supabase start` or `supabase status`.

```bash
export SUPABASE_URL=http://127.0.0.1:54321
export SUPABASE_SERVICE_ROLE_KEY=<local-service-role-key>
```

If another local Supabase stack is already bound to the ports, stop it before
starting `../sciona-infra`.

## Script Runtime

The ingestion scripts live in this repo under `scripts/`. They use the
`sciona.physics_ingest` package supplied by `sciona-matcher`. In a packaged
environment, install the `sciona` dependency normally. In the local monorepo
layout, the scripts automatically add `../sciona-matcher` to `sys.path` when
that sibling checkout exists.

The moved source-generation entrypoints are:

- `scripts/physics_ingest_wikidata_candidates.py`
- `scripts/physics_ingest_pdg_first_wave.py`
- `scripts/physics_inventory_pdg_remote.py`
- `scripts/physics_ingest_pdg_remote_wave.py`

`scripts/reseed_physics_supabase.py` replays already-curated seeds and does not
fetch remote source data.

## Curated Seed Reseed

The applied Wikidata and PDG ingestion rows are committed in this repo under:

```text
data/physics_ingestion_seeds/
```

The seed manifest pins replay order, row counts, source versions, and SHA-256
digests for each `write_plan.json` and `summary.json` artifact. The current
seed set contains 3,753 rows:

| Seed | Source version | Rows |
| --- | --- | ---: |
| `wikidata_physics_20260505` | `wikidata-physics-candidates-2026-05-05-limit-50` | 24 |
| `pdg_fixture_wave1_20260505` | `pdg-first-wave-2026-05-05` | 24 |
| `pdg_remote_wave1_20260505` | `pdg-remote-wave1-2026-05-05` | 714 |
| `pdg_remote_wave2_20260505` | `pdg-remote-wave2-2026-05-05` | 583 |
| `pdg_remote_wave3_20260505` | `pdg-remote-wave3-2026-05-05` | 489 |
| `pdg_remote_wave4_20260505` | `pdg-remote-wave4-2026-05-05` | 449 |
| `pdg_remote_wave5_20260505` | `pdg-remote-wave5-2026-05-05` | 318 |
| `pdg_remote_wave6_20260505` | `pdg-remote-wave6-2026-05-05` | 393 |
| `pdg_remote_wave7_20260505` | `pdg-remote-wave7-2026-05-05` | 759 |

Replay all committed seeds from `sciona-atoms-physics`:

```bash
export SUPABASE_URL=http://127.0.0.1:54321
export SUPABASE_SERVICE_ROLE_KEY=<local-service-role-key>
python scripts/reseed_physics_supabase.py
```

Inspect without writing:

```bash
python scripts/reseed_physics_supabase.py --list
python scripts/reseed_physics_supabase.py --dry-run
```

Replay a single seed:

```bash
python scripts/reseed_physics_supabase.py --only pdg_remote_wave7_20260505
```

The reseed script verifies artifact checksums before writing and replays each
write-plan batch through PostgREST upserts using the conflict keys embedded in
the write plan. It is idempotent for the committed seed rows.

Script-generated scratch artifacts should be written under `output/`, which is
ignored in this repo.

## Wikidata Equation Query

The current Wikidata candidate source is physics scoped. It starts from
Wikidata items that carry equation-like math and are classified under either
`Physics equations` or `physical law`, instead of importing every item with a
formula property. This keeps the first backfill focused while still preserving
raw source evidence for later expansion.

The query builder and response parser live in
`sciona.physics_ingest.sources.wikidata`. To refresh a candidate list, use the
retrieval adapter or call the builder directly:

```bash
python - <<'PY'
from pathlib import Path
import json

from sciona.physics_ingest.sources.wikidata import (
    build_physics_ingestion_candidate_query,
    build_wave0_candidate_records,
    execute_sparql_query,
)

out = Path("output/physics_wikidata_physics_candidate_list_manual")
out.mkdir(parents=True, exist_ok=True)
query = build_physics_ingestion_candidate_query(limit=50)
response = execute_sparql_query(query)
records = build_wave0_candidate_records(response)

(out / "query.sparql").write_text(query, encoding="utf-8")
(out / "response.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
(out / "wave0_candidate_records.json").write_text(
    json.dumps(records, indent=2),
    encoding="utf-8",
)
print(f"wrote {len(records)} candidates to {out}")
PY
```

The last reviewed candidate list is:

```text
output/physics_wikidata_physics_candidate_list_20260505T001957Z/
```

It contains 23 distinct physics equation candidates from 50 live source
bindings.

## Wikidata Upsert

Build and optionally apply the write plan with:

```bash
python scripts/physics_ingest_wikidata_candidates.py \
  --candidate-dir output/physics_wikidata_physics_candidate_list_20260505T001957Z \
  --out-dir output/physics_wikidata_physics_ingestion_local_apply_20260505T001957Z \
  --apply
```

The runner creates:

- `physics_ingest_snapshots`: one deterministic source snapshot row.
- `physics_equation_candidates`: one deterministic candidate row per Wikidata
  equation candidate.

Both tables are written with upsert mode using the conflict metadata in
`sciona.physics_ingest.write_plan.CONFLICT_KEYS_BY_TABLE`.

Generated artifacts include `source_bundle.json`, `planned_source_bundle.json`,
`write_plan.json`, `insert_rows_by_table.json`, `backfill_report.json`,
`apply_report.json`, `summary.json`, and `ingestion_template_learnings.md`.

After applying, verify the local database with:

```bash
python - <<'PY'
import psycopg

run_snapshot = "d66a5026-a727-5223-954d-561c0b90baa8"
conn = psycopg.connect("postgresql://postgres:postgres@127.0.0.1:54322/postgres")
with conn, conn.cursor() as cur:
    cur.execute(
        "select count(*) from physics_ingest_snapshots where snapshot_id = %s",
        (run_snapshot,),
    )
    print("snapshot_rows_for_run", cur.fetchone()[0])
    cur.execute(
        "select count(*) from physics_equation_candidates where snapshot_id = %s",
        (run_snapshot,),
    )
    print("candidate_rows_for_run", cur.fetchone()[0])
PY
```

The first local apply on May 5, 2026 inserted/upserted one snapshot and 23
candidate rows.

## PDG First Wave

The PDG path starts from already retrieved Physics Derivation Graph payloads.
The adapter intentionally does not fetch PDG content; it parses source payloads
into equation nodes and premise-to-conclusion inference edges.

Run the first local wave through source candidates, symbolic expression rows,
PDG relationship rows, and CDG rows with:

```bash
python scripts/physics_ingest_pdg_first_wave.py --apply
```

By default the runner uses:

```text
data/physics_ingestion_fixtures/pdg_payloads/solve_substitute_chain.pdg.json
```

The write includes:

- `physics_ingest_snapshots` and `physics_equation_candidates` for the PDG
  payload and its equation nodes.
- minimal `artifacts` and `artifact_versions` for each equation expression.
- `artifact_symbolic_expressions` for the equation nodes. These are preserved as
  symbolic equation rows even when full SymPy normalization is still pending.
- `artifact_relationships` for PDG derivation edges.
- `artifacts` and `artifact_versions` for the generated PDG-derived CDG.
- `artifact_cdg_nodes`, `artifact_cdg_edges`, and `artifact_cdg_bindings` for the
  derivation graph.

Catalog projection rows are intentionally not applied in this wave because the
current local schema exposes `catalog_symbolic_artifacts` as a read-only view.
The CDG itself is still materialized in the unified artifact and CDG tables.

## PDG Remote Inventory

Before ingesting the remote PDG corpus, generate an immutable inventory of the
upstream repository tree and classify files/derivations into staged ingestion
waves. The inventory runner is conservative by default: it uses the GitHub API,
sends an explicit `User-Agent`, spaces requests, and stops optional fetches when
the remaining quota reaches the configured reserve.

For higher GitHub API quota, authenticate the local `gh` client before running
PDG scripts:

```bash
gh auth login
gh auth status
```

The PDG inventory and promotion runners resolve credentials in this order:
`--github-token-env` (default `GITHUB_TOKEN`), `GH_TOKEN`, then `gh auth token`.
They record only the credential source in output summaries, not the token value.
Use `--no-gh-auth-token` to force anonymous calls when env vars are unset.

```bash
python scripts/physics_inventory_pdg_remote.py \
  --repo allofphysicsgraph/ui_v8_website_flask_neo4j \
  --ref gh-pages \
  --license-expression CC-BY-4.0 \
  --fetch-core-files \
  --min-delay-seconds 2 \
  --max-requests 8 \
  --rate-limit-reserve 10
```

The runner writes:

- `pdg_remote_inventory_manifest.json`: complete inventory envelope.
- `tree_inventory.json`: repository file roles and raw-ingestion candidates.
- `core_file_analysis.json`: parsed Cypher node/relationship counts and rule
  classifications when core files are fetched.
- `pdg_derivations_inventory.json`: derivation-level rows with step counts,
  input/output expression counts, operation-kind counts, readiness scores, and
  recommended waves.
- `ingestion_waves.json` and `PDG_REMOTE_INGESTION_WAVES.md`: actionable wave
  plan for raw preservation and later symbolic/CDG promotion.
- `rate_limit_report.json`: request URLs, statuses, durations, and GitHub
  rate-limit headers.

Selection policy:

- preserve every license-allowed PDG resource as raw source evidence,
- promote first derivations with graph-complete steps, input/output
  expressions, and recognized operation kinds,
- keep derivations with weaker structure as relationship candidates or
  metadata-only candidates rather than dropping them,
- defer notebooks, web app support, Docker files, and test artifacts unless
  they carry provenance needed by a source snapshot.

## PDG Remote Promotion Wave

After inventory, promote a small representative set of remote derivations
through source candidates, symbolic expression rows, relationship rows, and
one CDG artifact per derivation.

```bash
python scripts/physics_ingest_pdg_remote_wave.py \
  --repo allofphysicsgraph/ui_v8_website_flask_neo4j \
  --ref gh-pages \
  --derivation-id 000008 \
  --derivation-id 000009 \
  --derivation-id 000018 \
  --derivation-id 129143 \
  --derivation-id 000004 \
  --min-delay-seconds 2 \
  --max-requests 7 \
  --rate-limit-reserve 10 \
  --apply
```

The runner fetches only repository metadata and the six core Cypher graph files:
`deriv.cypher`, `infrules.cypher`, `operators.cypher`, `steps.cypher`,
`expr_and_feed.cypher`, and `symbols.cypher`. It converts selected derivation
steps into premise-to-conclusion PDG edges and preserves feed values in edge
binding metadata. Expression rows remain `needs_human`/`unknown` until symbolic
normalization and dimensional validation are explicitly completed.

## PDG Remote Waves Ingested

The remote PDG inventory was built from
`allofphysicsgraph/ui_v8_website_flask_neo4j` at `gh-pages`. The active remote
repository advertises CC-BY-4.0 provenance through the PDG developer
documentation, and the promotion scripts record `CC-BY-4.0` on source snapshots
and payloads.

The remote inventory detected 44 derivations with parseable graph structure.
So far, 35 remote derivations have been promoted through symbolic expression
rows, PDG relationship rows, and CDG rows across seven applied waves.

| Wave | Derivations | Symbolic rows | Relationships | CDG nodes | CDG edges | CDG bindings |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `pdg_remote_wave1_20260505` | `000008`, `000009`, `000018`, `129143`, `000004` | 80 | 83 | 83 | 51 | 166 |
| `pdg_remote_wave2_20260505` | `000001`, `000006`, `142831`, `146432`, `884319` | 64 | 67 | 67 | 49 | 133 |
| `pdg_remote_wave3_20260505` | `000005`, `000011`, `000015`, `670255`, `513999` | 57 | 52 | 53 | 39 | 106 |
| `pdg_remote_wave4_20260505` | `000002`, `000003`, `000007`, `000012`, `000013` | 49 | 51 | 52 | 35 | 104 |
| `pdg_remote_wave5_20260505` | `000014`, `000016`, `000017`, `375160`, `681943` | 36 | 35 | 35 | 23 | 70 |
| `pdg_remote_wave6_20260505` | `909006`, `918264`, `920011`, `387954`, `527822` | 46 | 43 | 43 | 26 | 86 |
| `pdg_remote_wave7_20260505` | `282755`, `522862`, `608598`, `764666`, `820976` | 89 | 84 | 84 | 56 | 168 |

Wave 3 originally tested `207210` (`Newton's Law of Gravitation`) but deferred
it because the current parser saw missing expression endpoints on eight edges.
It should be revisited after the remote Cypher endpoint handling is broadened.

The latest wave, `pdg_remote_wave7_20260505`, promoted:

- `282755`: radius for satellite in geostationary orbit
- `522862`: optics, law of refraction to Brewster's angle
- `608598`: upper limit on velocity in condensed matter
- `764666`: Langmuir adsorption
- `820976`: Kepler's Third Law, period squared proportional to distance cubed

The wave 7 dry run and apply both completed with zero graph diagnostics and
zero skipped PDG edges. The apply used authenticated GitHub requests via
`gh-auth-token`; the last observed remaining quota was 4,916 requests.
