# Detector Corrections Atoms - Review Bundle

## Summary

Three atoms ported from the TrackML 5th-place solution (Steiner, 2018) implementing
coordinate rescaling for k-NN searches and perturbative displacement corrections
at helix-detector surface intersections:

1. **coordinate_rescaling_for_knn** - Project 3D hit positions onto reference cylinder
   with z-scale normalization for meaningful k-NN distances
2. **perturbative_cap_correction** - Radial/azimuthal displacement corrections at
   cap (z-plane) intersections, scaled by charge and pitch
3. **perturbative_cylinder_correction** - Azimuthal and z-displacement corrections at
   cylinder intersections, scaled by charge and curvature radius

## Source Files

- `neighbors.py:84-97` (transformToNeighborCoords)
- `corrections.py:181-238` (correctCapIntersections)
- `corrections.py:240-307` (correctCylinderIntersections)

## License

BSD-2-Clause (https://github.com/edwinst/trackml_solution)
