# pulsar_folding remainder review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/pulsar_folding_review_bundle.json`
Rows covered: 3
Ready rows: 3
Conditional rows: 0

## Authoritative sources
- `lorimer2005pulsar`: Broad pulsar-search background covering dispersion, folding, and profile detection context.
- `repo_pulsar_folding`: Upstream Pulsar_Folding software attribution.

## Scope notes
- Scope is limited to the unpublished remainder atoms `sciona.atoms.physics.pulsar_folding.dm_can.dm_candidate_filter`, `sciona.atoms.physics.pulsar_folding.dm_can_brute_force`, and `sciona.atoms.physics.pulsar_folding.spline_bandpass_correction`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, and direct behavior checks.
- `dm_candidate_filter` is reviewed against the wrapper's concrete one-score-per-candidate contract rather than a pruned candidate-subset contract.
- `dm_can_brute_force` is reviewed against the wrapper's "return the best rolled profile" contract.
- `spline_bandpass_correction` is reviewed against the wrapper's baseline-subtraction contract.
