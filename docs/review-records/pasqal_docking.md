# Pasqal docking review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/pasqal_docking_review_bundle.json`
Rows covered: 2
Ready rows: 2
Conditional rows: 0

## Authoritative sources
- `moleculardocking2025`: Pasqal molecular-docking workflow attribution.

## Scope notes
- Scope is limited to `sciona.atoms.physics.pasqal.docking.graph_transformer` and `sciona.atoms.physics.pasqal.docking.sub_graph_embedder`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, reference attribution, and direct behavior checks.
- `quantum_mwis_solver` is intentionally held out because the implementation describes itself as a deterministic placeholder heuristic rather than a reviewed quantum solver.
- `graph_transformer` is reviewed as the wrapper's concrete lattice-edge filtering transform, not as a full molecular docking graph placement algorithm.
- `sub_graph_embedder` is reviewed as the wrapper's deterministic sorted-node singleton mapping helper, not as a complete subgraph isomorphism or lattice embedding algorithm.
