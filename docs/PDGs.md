# Physics Derivation Graphs

This document describes the Physics Derivation Graph (PDG) data now curated in
Sciona. It is intended as conceptual context for agents that need to understand
what the PDG-derived rows represent, where they came from, and why the ingested
CDG rows are normalized the way they are.

## What PDGs Are

A Physics Derivation Graph is a source graph of physics derivations. Conceptually,
it represents a derivation as:

- equation-like nodes, such as `F = m a` or `F \propto m_1 m_2 / r^2`;
- derivation step nodes, each tied to an inference rule such as `substitute`,
  `simplify`, `differentiate`, `integrate`, or `derive`;
- directed relationships from premise expressions to output expressions;
- feed/binding values used by individual steps, such as variable names,
  substitutions, or other values used by an inference rule.

The useful conceptual model is:

```text
premise expression(s) --[PDG step / inference rule]--> output expression(s)
```

The PDG is external knowledge. It is not authored as native Sciona atoms, and
its expressions are not assumed to be fully parsed, dimensionally validated, or
reviewed when first imported. Sciona preserves the raw source provenance while
also projecting the derivation structure into symbolic expression rows,
relationship rows, and computational derivation graph (CDG) rows.

## Source

The remote PDG corpus ingested so far came from:

```text
GitHub repo: allofphysicsgraph/ui_v8_website_flask_neo4j
Git ref:     gh-pages
```

The ingestion scripts fetch repository metadata and the core Cypher export files:

```text
conversion_of_data_formats/deriv.cypher
conversion_of_data_formats/infrules.cypher
conversion_of_data_formats/operators.cypher
conversion_of_data_formats/steps.cypher
conversion_of_data_formats/expr_and_feed.cypher
conversion_of_data_formats/symbols.cypher
```

Those files encode derivation nodes, inference rules, step membership, expression
and feed nodes, and step-to-expression relationships. The current remote source
snapshot records `CC-BY-4.0` provenance.

The curated seed artifacts live in:

```text
data/physics_ingestion_seeds/
```

The authoritative seed ordering, checksums, source versions, selected derivation
IDs, and row counts are in:

```text
data/physics_ingestion_seeds/manifest.json
```

As of the normalized seed set, Sciona has promoted all 44 parseable remote PDG
derivations across ten remote waves. The remote PDG seeds contain 5,680 rows;
the full physics ingestion seed set also includes Wikidata and local PDG fixture
rows.

## Ingestion Shape

For each selected remote derivation wave, the ingestion pipeline builds:

- `physics_ingest_snapshots`: immutable source snapshot and provenance metadata.
- `physics_equation_candidates`: raw equation candidates from PDG expression
  endpoints.
- `artifacts`, `artifact_versions`, and `artifact_symbolic_expressions`: draft
  symbolic equation artifacts for each PDG expression endpoint.
- `artifact_relationships`: raw derivation relationships from output expression
  back to premise expression, preserving PDG edge evidence.
- `artifact_cdg_nodes`, `artifact_cdg_edges`, and `artifact_cdg_bindings`: a
  normalized CDG projection of the derivation steps.

The symbolic expression rows are intentionally conservative:

- `parse_status` is `raw_imported`;
- `review_status` is `needs_human`;
- `validation_status` is `unknown`;
- raw LaTeX/SymPy/source payloads are preserved for later normalization and
  dimensional validation.

## Endpoint Handling

Most PDG step inputs and outputs point to source nodes labelled `expression`.
Some remote derivations use nodes labelled `feed` as expression endpoints even
though the step graph references those IDs as expression inputs or outputs. The
Newton's Law of Gravitation derivation (`207210`) exposed this pattern.

Sciona handles that source inconsistency as follows:

- if a `feed` node is used as a step input or output endpoint, it is promoted as
  a symbolic equation candidate;
- the promoted row records `pdg_node_label: feed` in provenance;
- ordinary `HAS_FEED` values that are not expression endpoints remain binding
  metadata on the relevant derivation edge.

This keeps derivation endpoints complete without pretending that every feed node
is automatically an equation.

## Relationship Direction

Source PDG edges are premise-to-conclusion:

```text
premise expression -> conclusion expression
```

Sciona `artifact_relationships` use the relationship-row convention that the
derived expression is the source and the dependency/premise is the target:

```text
conclusion expression derives_from premise expression
```

The raw PDG edge ID, source node ID, target node ID, inference rule ID, operation
kind, and source evidence are preserved in row metadata.

## CDG Normalization

The raw PDG relationship layer preserves one row per premise-to-conclusion PDG
edge. That is important provenance and should not be collapsed.

The CDG projection is intentionally more compact. It groups relationship edges
that share the same source PDG step ID (`pdg_step_id` or `step_id`) into one CDG
operation node:

```text
raw PDG relationships:
  A -> C  step S
  B -> C  step S

normalized CDG:
  node S: operation(input_expressions=[A, B], output_expressions=[C])
```

This normalization matters because many PDG inference rules are multi-input
operations. Without grouping, one source derivation step with several inputs
would become several separate CDG operation nodes, overstating the number of
operations and obscuring the actual mechanism.

The normalized CDG projection:

- keeps all raw `artifact_relationships` intact;
- creates one CDG node per source PDG step when step metadata is present;
- attaches all premise expression bindings to that CDG node;
- attaches all output expression bindings to that CDG node;
- records `source_pdg_step_id`, `source_pdg_inference_ids`, and `pdg_edge_ids`
  in the node type signature/provenance;
- creates CDG edges only for dataflow between operation nodes, when one step
  consumes an expression produced by an earlier step.

If a source edge has no step ID, the projection falls back to one CDG node per
edge so no derivation information is lost.

## How To Read The Rows

When inspecting PDG-derived data, use these heuristics:

- `artifact_relationships` answer: "What raw source derivation edges exist?"
- `artifact_cdg_nodes` answer: "What derivation operations should execute or be
  reasoned about as steps?"
- `artifact_cdg_bindings` answer: "Which symbolic expression artifacts are
  inputs or outputs of each CDG operation?"
- `physics_equation_candidates` and `artifact_symbolic_expressions` answer:
  "Which raw equations were imported and still need symbolic/dimensional review?"

Do not treat a PDG-derived symbolic expression as reviewed physics truth just
because it is present. The current import establishes provenance, structure, and
reviewable external knowledge. Later symbolic normalization, dimensional
validation, and human review determine whether a row is publishable as a trusted
Sciona physics atom.

## Regeneration

The remote PDG source-generation script is:

```text
scripts/physics_ingest_pdg_remote_wave.py
```

The committed seeds can be replayed without contacting the remote source:

```text
scripts/reseed_physics_supabase.py
```

See `PHYSICS_INGESTION.md` for operational commands, local Supabase setup, seed
counts, and current ingestion status.
