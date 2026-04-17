# pulsar pipeline review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/pulsar_pipeline_review_bundle.json`
Rows covered: 4
Ready rows: 4
Conditional rows: 0

## Authoritative sources
- `lorimer2005pulsar`: Broad pulsar-search background covering dispersion, folding, and profile detection context.

## Scope notes
- Scope is limited to the four wrappers in `sciona.atoms.physics.pulsar.pipeline`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, and direct behavior checks.
- `SNR` is reviewed against the wrapper's explicit `log(peak / abs(mean(profile)))` contract rather than a variance-normalized radio-astronomy S/N convention.
