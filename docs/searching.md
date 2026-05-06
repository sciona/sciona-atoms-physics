# Symbolic Expression Searching

This document describes the heuristic funnel system for matching empirical
datasets against the symbolic physics atoms curated in Sciona. It is the
implementation companion to `searching.pdf`, which describes the design
rationale. Agents should read this document to understand how the funnel
works, what index fields it relies on, and where the code lives.

## Problem

Matching a dataset against thousands of intermediate symbolic expressions
from the Physics Derivation Graphs (PDGs) is computationally prohibitive
with iterative curve fitting. Levenberg-Marquardt requires initial guesses,
gets stuck in local minima, and costs O(N·K) per candidate where K is the
number of unknown constants.

## Solution: Heuristic Funnel

A deterministic, multi-stage filter that uses O(1) metadata checks and O(N)
vectorized arithmetic to eliminate non-matches, reserving expensive numerical
fits for the final <1% of candidates.

The funnel runs as a pre-filter in the Hunter round of sciona-matcher. When
a high-confidence match is found, it short-circuits the full LLM-based
matching pipeline.

## Index Fields

Three pre-computed fields on each `artifact_symbolic_expressions` row enable
the funnel's O(1) lookups. These are computed during the publication manifest
build in `symbolic_publication_manifest.py`.

### `equivalence_class_hash`

Groups algebraically identical forms into one equivalence class. `F = ma`,
`a = F/m`, and `F - ma = 0` all share the same hash. The funnel only tests
one representative per class, collapsing 87 expressions to 37 unique
surfaces.

Implementation: `cancel(lhs - rhs)` → extract numerator → `expand` → monic
polynomial → positional-placeholder symbols → SHA-256.

### `exponent_signature` / `exponent_signature_hash`

For monomial (power-law) expressions, records the rational exponent of each
data-backed variable. Example:

```
t = K · DM · f⁻²  →  {"DM": "1", "f": "-2"}
```

The runtime extracts exponents from the dataset via log-space SVD and does an
O(1) hash lookup against these indexed signatures.

Returns `null` for non-monomial expressions (those containing `sin`, `log`,
`Add`, etc.). Currently 13 of 87 expressions have exponent signatures.

### `invariant_forms`

For each isolatable constant in the expression, stores a pre-computed
invariant expression over data-only variables. Example:

```
delay = K · DM / f²  →  K = delay · f² / DM
invariant_expr: "delay*f**2/DM"
```

The runtime evaluates this invariant vectorized over dataset rows. If the
coefficient of variation (CV = σ/|μ|) is near zero, the law holds and μ is
the fitted constant. Currently 36 of 87 expressions have invariant forms.

## Funnel Stages

The stages run in cascade order. Each stage is a pure function in
`sciona-matcher/sciona/symbolic_funnel/stages.py`.

### Stage 0: Spectral Dimensionality Gate (O(ND² + D³))

Pre-gates the entire funnel from running on structureless data. Computes the
**participation ratio** (PR) of the eigenvalue spectrum of the standardized
covariance matrix:

```
PR = (Σλ)² / Σλ²
```

PR ≈ D means a uniform blob (all columns independent); PR < D means
inter-column structure exists. Runs on both raw and log-transformed data so
power-law relationships with wide dynamic range still pass. Gate closes when
both PR values exceed D − 0.5.

### Stage 1: Boundary Triage (O(1) per candidate)

Reject candidates whose required variables are missing from the dataset, whose
validity bounds are violated by column ranges, or whose dimensional signatures
are incompatible. Only equivalence class representatives are tested.

### Stage 2: Exponent Extraction (O(N) once, then O(1) per lookup)

Take `np.log` of all positive columns, compute the covariance matrix, run SVD.
The null-space vector yields the power-law exponent fingerprint. Snap
exponents to nearest rationals, hash, and look up in the index's
`by_exponent_hash` table. Non-power-law candidates pass through unfiltered.

### Stage 3: Invariant Variance (O(N) per surviving candidate)

For each candidate with pre-computed `invariant_forms`, AOT-compile the
invariant expression to a NumPy callable via `SymbolicExpression.to_numpy_lambda()`,
evaluate vectorized over dataset rows, compute CV. If CV < threshold (default
0.05), the law holds and `mean(result)` is the fitted constant.

### Stage 4: Graph-Directed Constraint Propagation (conditional)

Only runs when CDG context is available (`artifact_relationships`,
`artifact_cdg_nodes`). Tests root premise equations first; if a root fails,
prunes the entire downstream subgraph. For missing variables, if a CDG edge
indicates `differentiate(x, t)`, synthesizes the variable via `np.gradient`.

### Stage 5: Multi-Fidelity RANSAC (final survivors only)

For non-linearizable expressions or those without invariant forms. Samples K+1
rows (K = number of unknown constants), solves the exact algebraic system,
evaluates residual on 50 random holdout points. Full least-squares only on
candidates with low RANSAC residual.

## Heuristic Integration

The funnel produces six canonical heuristic IDs registered in
`sciona-matcher/sciona/heuristics.py`:

| Heuristic ID | Evidence Type | Description |
|---|---|---|
| `spectral_dimensionality_gate` | `scalar_score` | Participation ratio of eigenvalue spectrum |
| `boundary_triage_pass` | `boolean_flag` | Validity bounds and dimensional compatibility |
| `exponent_signature_match` | `boolean_flag` | SVD exponent fingerprint matches indexed signature |
| `invariant_variance_cv` | `scalar_score` | Coefficient of variation of invariant expression |
| `ransac_fit_residual` | `scalar_score` | Normalized median residual from RANSAC fit |
| `graph_pruning_depth` | `scalar_score` | Number of CDG nodes pruned by root failure |

The heuristic bridge in `sciona/symbolic_funnel/heuristic_bridge.py` converts
`FunnelResult` objects into `RuntimeHeuristicObservation` instances that flow
into the existing telemetry and heuristic outcome tracking system.

## File Locations

**sciona-atoms-physics:**

```
src/sciona/atoms/physics/symbolic_publication_manifest.py
  _canonical_zero_form()     equivalence class hashing
  _exponent_signature()      power-law exponent extraction
  _invariant_forms()         constant isolation
tests/test_funnel_index_fields.py   12 tests
```

**sciona-matcher:**

```
sciona/symbolic_funnel/
  __init__.py
  dataset.py          EmpiricalDataset model
  contracts.py        FunnelConfig, StageVerdict, FunnelCandidate, FunnelResult
  index.py            FunnelIndex loaded from publication manifests
  stages.py           6 stages as pure functions + run_funnel() orchestrator
  heuristic_bridge.py CanonicalHeuristic definitions + bridge functions
sciona/heuristics.py  6 new canonical heuristic IDs
tests/test_symbolic_funnel/
  conftest.py                    synthetic data generators for 5 laws
  test_stage_spectral_gate.py    13 tests
  test_stage_boundary_triage.py   4 tests
  test_stage_exponent_extraction.py  4 tests
  test_stage_invariant_variance.py   7 tests
  test_funnel_e2e.py                 9 tests
```

## Current Coverage

As of the last manifest build:

- 87 symbolic expressions → 37 unique equivalence classes (57% reduction)
- 13 expressions with exponent signatures (power-law monomials)
- 36 expressions with invariant forms (isolatable constants)
- 37 tests across both repos, all passing in < 0.5 seconds
