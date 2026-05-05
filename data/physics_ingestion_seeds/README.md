# Physics Ingestion Seeds

This directory contains curated Supabase reseed artifacts generated from the
physics ingestion work in `sciona-matcher`.

Each seed directory contains:

- `write_plan.json`: ordered table batches with rows and conflict keys.
- `summary.json`: source-version, row-count, and provenance summary from the
  original apply run.

`manifest.json` pins the replay order and SHA-256 digests for every artifact.
The reseed script verifies these digests before writing.

Replay into a local Supabase instance:

```bash
export SUPABASE_URL=http://127.0.0.1:54321
export SUPABASE_SERVICE_ROLE_KEY=<local-service-role-key>
python scripts/reseed_physics_supabase.py
```

Inspect without writing:

```bash
python scripts/reseed_physics_supabase.py --dry-run
python scripts/reseed_physics_supabase.py --list
```

Replay one seed:

```bash
python scripts/reseed_physics_supabase.py --only pdg_remote_wave4_20260505
```
