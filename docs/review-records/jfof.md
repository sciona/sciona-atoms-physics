# jFOF review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/jfof_review_bundle.json`
Rows covered: 2
Ready rows: 2
Conditional rows: 0

## Authoritative sources
- `huchra1982fof`: Friends-of-friends clustering attribution.
- `repo_jfof`: Upstream jFOF software attribution.

## Scope notes
- Scope is limited to `sciona.atoms.physics.jFOF.find_fof_clusters` and `sciona.atoms.physics.jFOF.topo.topological_loss_computation`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, and direct behavior checks.
- `topological_loss_computation` is reviewed against the wrapper's concrete scalar-loss contract with scalar `max_iters` and `tau`.
