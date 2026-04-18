# astroflow review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/astroflow_review_bundle.json`
Rows covered: 1
Ready rows: 1
Conditional rows: 0

## Authoritative sources
- `astroflow2025`: Primary AstroFlow paper.
- `repo_astroflow`: Upstream AstroFlow software attribution.

## Scope notes
- Scope is limited to `sciona.atoms.physics.astroflow.dedispersionkernel`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, and direct behavior checks.
- The witness now publishes the concrete 2D output signal contract with shape `(dm_steps, down_ndata)`.
