from __future__ import annotations

from sciona.ghost.dimensions import DIMENSIONLESS, DimensionalSignature
from sciona.ghost.registry import REGISTRY


def _load_helix_atoms() -> None:
    import sciona.atoms.particle_tracking.helix_geometry.atoms  # noqa: F401


def test_helix_geometry_atoms_register_symbolic_metadata() -> None:
    _load_helix_atoms()

    expected = {
        "circle_from_three_points",
        "helix_pitch_from_two_points",
        "helix_pitch_least_squares",
        "helix_direction_from_two_points",
        "helix_nearest_point_distance",
    }
    for name in expected:
        entry = REGISTRY[name]
        symbolic = entry["symbolic"]
        assert symbolic is not None, name
        assert symbolic.check_dimensional_consistency() == []


def test_radius_pitch_angle_and_distance_dimensions_are_registered() -> None:
    _load_helix_atoms()

    length = DimensionalSignature(L=1)
    area = DimensionalSignature(L=2)

    circle_dims = REGISTRY["circle_from_three_points"]["dim_signature"]
    assert circle_dims["r"] == length
    assert circle_dims["large_radius"] == length

    pitch_dims = REGISTRY["helix_pitch_from_two_points"]["dim_signature"]
    assert pitch_dims["hel_pitch"] == length
    assert pitch_dims["phid"] == DIMENSIONLESS
    assert pitch_dims["dz"] == length

    least_squares_dims = REGISTRY["helix_pitch_least_squares"]["dim_signature"]
    assert least_squares_dims["hel_pitch"] == length
    assert least_squares_dims["loss"] == area

    distance_dims = REGISTRY["helix_nearest_point_distance"]["dim_signature"]
    assert distance_dims["hel_r"] == length
    assert distance_dims["dist"] == length
    assert distance_dims["iterations"] == DIMENSIONLESS


def test_validity_bounds_cover_positive_radius_pitch_regularizer_and_distance() -> None:
    _load_helix_atoms()

    circle_symbolic = REGISTRY["circle_from_three_points"]["symbolic"]
    assert circle_symbolic.validity_bounds["r"] == (0.0, None)
    assert circle_symbolic.validity_bounds["large_radius"] == (0.0, None)

    pitch_symbolic = REGISTRY["helix_pitch_from_two_points"]["symbolic"]
    assert pitch_symbolic.validity_bounds["zero_pitch"] == (0.0, None)
    assert pitch_symbolic.validity_bounds["phid"][0] < 0.0
    assert pitch_symbolic.validity_bounds["phid"][1] > 0.0

    distance_symbolic = REGISTRY["helix_nearest_point_distance"]["symbolic"]
    assert distance_symbolic.validity_bounds["hel_r"] == (0.0, None)
    assert distance_symbolic.validity_bounds["dist"] == (0.0, None)
    assert distance_symbolic.validity_bounds["iterations"] == (1.0, None)
