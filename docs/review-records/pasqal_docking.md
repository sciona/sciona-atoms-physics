# Pasqal docking review record

Provider slice: `sciona-atoms-physics`
Bundle: `docs/review-bundles/pasqal_docking_review_bundle.json`
Rows covered: 3
Ready rows: 3
Conditional rows: 0

## Authoritative sources
- `moleculardocking2025`: Pasqal molecular-docking workflow attribution.

## Scope notes
- Scope covers `sciona.atoms.physics.pasqal.docking.graph_transformer`, `sciona.atoms.physics.pasqal.docking.sub_graph_embedder`, and `sciona.atoms.physics.pasqal.docking.quantum_mwis_solver`.
- Review is based on local wrapper and witness source, deterministic metadata, import smoke, reference attribution, and direct behavior checks.
- `quantum_mwis_solver` delegates to the optional Pulser/emulator backend lane documented in `docs/quantum_optional_dependencies.md`; base imports remain lightweight and runtime execution requires the `quantum` optional dependency group.
- `graph_transformer` is reviewed as the wrapper's concrete lattice-edge filtering transform, not as a full molecular docking graph placement algorithm.
- `sub_graph_embedder` is reviewed as the wrapper's deterministic sorted-node singleton mapping helper, not as a complete subgraph isomorphism or lattice embedding algorithm.
