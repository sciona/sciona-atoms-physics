# Phase 4: Physics Atom Migration to `@symbolic_atom`

## Context

Phases 1-3 (implemented in `sciona-matcher`) introduced:
- `DimensionalSignature` type system with 7 SI base exponents (`sciona/ghost/dimensions.py`)
- `SymbolicExpression` model for SymPy AST storage (`sciona/ghost/symbolic.py`)
- `@symbolic_atom` decorator combining SymPy expressions, dimensional analysis, and `@register_atom` (`sciona/ghost/decorators.py`)
- Dimensional analysis enforcement in the compiler (`sciona/synthesizer/dim_checker.py`)

This plan migrates all 93 atoms in `sciona-atoms-physics` to use `@symbolic_atom` with full dimensional signatures, SymPy expressions, validity bounds, and named constants.

---

## Inventory

| Module | atoms.py | witnesses.py | @register_atom count |
|--------|----------|-------------|---------------------|
| `physics/astroflow/` | Yes | Yes | 1 |
| `physics/jFOF/` | Yes | Yes | 1 |
| `physics/pulsar/` | pipeline.py | Yes | 0 (pipeline-level, no atoms) |
| `physics/pulsar_folding/` | Yes + dm_can.py | Yes + dm_can_witnesses.py | 2 |
| `physics/skyfield/` | Yes | Yes | 2 |
| `physics/tempo_jl/` | Yes | Yes | 2 |
| `physics/tempo_jl/apply_offsets/` | Yes | Yes | 3 |
| `physics/tempo_jl/find_month/` | Yes | Yes | 10 |
| `physics/tempo_jl/find_year/` | Yes | Yes | 15 |
| `physics/tempo_jl/jd2cal/` | Yes | Yes | 10 |
| `physics/tempo_jl/offsets/` | Yes | Yes | 3 |
| `physics/tempo_jl/tai2utc/` | Yes | Yes | 15 |
| `physics/tempo_jl/tai2utc_d12/` | Yes | Yes (partial) | 2 |
| `physics/tempo_jl/utc2tai/` | Yes | Yes | 15 |
| `physics/pasqal/` | docking.py | docking_witnesses.py | (Pydantic state, not @register_atom) |
| `particle_tracking/detector_corrections/` | Yes | Yes | 3 |
| `particle_tracking/helix_geometry/` | Yes | Yes | 5 |
| `particle_tracking/track_matching/` | Yes | Yes | 4 |
| **Total** | | | **93** |

---

## New Files to Create

### `src/sciona/atoms/physics/dimensions.py`
Centralised domain-specific dimensional constants and named physical constants.

```python
from sciona.ghost.dimensions import (
    DimensionalSignature, DIMENSIONLESS, SECOND, METER, HERTZ, KILOGRAM,
)

# Astrophysics dimensions
TIME = SECOND
FREQUENCY = HERTZ
DISPERSION_MEASURE = DimensionalSignature(T=1, L=-2)  # pc·cm⁻³ (conventional)
FLUX_DENSITY = DimensionalSignature(M=1, T=-2)         # Jansky-like
POWER = DimensionalSignature(M=1, L=2, T=-3)

# Named constants (replacing magic numbers)
DISPERSION_CONSTANT = 4.148808e3   # MHz² pc⁻¹ cm³ s (pulsar_folding/dm_can.py:38)
PULSAR_DM_COEFF = 0.000241        # (pulsar/pipeline.py delay_from_DM)

# Particle tracking
LENGTH = METER
ANGLE = DIMENSIONLESS  # radians

# Time conversion
JULIAN_DAY = SECOND  # JD is a time measure
MJD_OFFSET = 2400000.5  # JD - MJD offset constant
```

### Per-subdirectory `expressions.py`
Each module gets an `expressions.py` that defines SymPy `Expr` objects for its atoms. This keeps SymPy imports isolated from the heavy implementation code.

Example for `pulsar_folding/expressions.py`:
```python
import sympy as sp

DM, freq, K = sp.symbols("DM freq K")
delay_expr = K * DM * freq**sp.Integer(-2)

# ... one expression per atom in the module
```

---

## Migration Order

### Wave 1: Pulsar (most physics-heavy, best test case)
1. `physics/pulsar_folding/` — 2 atoms, clear physics equations (DM delay, fold)
2. `physics/pulsar_folding/dm_can.py` — DM candidate filter with magic constant `4.148808e3`

### Wave 2: Particle Tracking (vector geometry)
3. `particle_tracking/helix_geometry/` — 5 atoms (circle fitting, pitch estimation, Kepler)
4. `particle_tracking/detector_corrections/` — 3 atoms (coordinate rescaling)
5. `particle_tracking/track_matching/` — 4 atoms

### Wave 3: Astrophysics
6. `physics/astroflow/` — 1 atom (GPU dedispersion kernel)
7. `physics/skyfield/` — 2 atoms (spherical coordinate transforms)

### Wave 4: Time Conversion (high volume, mechanical migration)
8. `physics/tempo_jl/` — 2 atoms + 8 submodules totalling 73 atoms
   - These are primarily arithmetic time-conversion atoms (UTC↔TAI, JD↔calendar)
   - Most are dimensionless or TIME→TIME, good candidates for batch migration script

### Wave 5: Specialised
9. `physics/jFOF/` — 1 atom (friends-of-friends clustering, graph-based)
10. `physics/pasqal/` — quantum docking (Pydantic state machine, may need `skip_dim_check`)

---

## Per-Module Migration Steps

For each module:

1. **Create `expressions.py`** — define SymPy expressions for each atom
2. **Modify `atoms.py`**:
   - Replace `@register_atom(witness_foo)` with `@symbolic_atom(witness=witness_foo, expr=..., dim_map=..., ...)`
   - Replace magic number constants with named constants from `dimensions.py`
   - Add `validity_bounds` where physics imposes constraints (e.g., DM >= 0, freq > 0)
   - Add `bibliography` references (Wikidata Q-items, DOIs from existing `references.json`)
3. **Modify `witnesses.py`**:
   - Add `dim=` parameter to all returned `AbstractSignal`, `AbstractArray`, `AbstractScalar` objects
   - Use constants from `dimensions.py`
4. **Run existing tests** — must pass unchanged
5. **Add dim integration test** — mini CDG connecting 2-3 atoms, verify dim checker passes

---

## pyproject.toml Changes

```toml
[project.optional-dependencies]
sympy = ["sympy>=1.12"]
```

Add `sympy>=1.12` to optional deps. It is only needed at registration/build time.

---

## Migration Script

Create `scripts/migrate_physics_atoms.py`:
- Scans all `witnesses.py` for `AbstractSignal(..., units="...")` / `AbstractScalar(...)` returns
- Uses `parse_units_string()` from `sciona.ghost.dimensions` to suggest `DimensionalSignature`
- For each `@register_atom` in `atoms.py`, generates a diff showing the `@symbolic_atom` replacement
- Outputs a per-module report for human review

---

## Verification

After each wave:
1. `pytest` in this repo — all existing tests pass
2. `pytest` in `sciona-matcher` — no regressions
3. For Wave 1 (pulsar): build a test CDG `dedisperse → fold → SNR` and run the dim checker end-to-end
4. For each subsequent wave: verify dim annotations are correct by cross-referencing `references.json` sources

---

## Estimated Effort

| Wave | Atoms | Complexity | Notes |
|------|-------|-----------|-------|
| 1 | 2 | Medium | Clear physics, good template for others |
| 2 | 12 | Medium | Vector geometry, well-typed |
| 3 | 3 | Low | Straightforward astrophysics |
| 4 | 73 | Low per-atom | Mechanical — batch migration script for time conversions |
| 5 | 3 | Medium | Special cases (graph algo, quantum) |
