# Track Matching Atoms - Review Bundle

## Summary

Four atoms ported from the TrackML 5th-place solution (Steiner, 2018) implementing
the core track propagation and candidate evaluation pipeline:

1. **helix_cylinder_intersection** - Helix-cylinder intersection via r^2 harmonic motion and arccos phase solve
2. **helix_cap_intersection** - Helix-cap (z-plane) intersection via linear z-phase relationship
3. **bayesian_neighbor_evaluation** - Error-normalized Bayesian cut for neighbor quality scoring
4. **greedy_track_commit** - Sequential greedy track commitment with hit deduplication

## Source Files

- `geometry.py:265-446` (CylinderIntersector.intersectHelices)
- `geometry.py:454-580` (CapIntersector.intersectHelices)
- `algorithm.py:292-371` (Algorithm.bayesianNeighborEvaluation)
- `candidates.py:44-99` (zeroUsedHits)

## License

BSD-2-Clause (https://github.com/edwinst/trackml_solution)
