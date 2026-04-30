from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, DimensionalSignature
from sciona.ghost.registry import REGISTRY


def _load_skyfield_atoms() -> None:
    import sciona.atoms.physics.skyfield.atoms  # noqa: F401


def test_skyfield_atoms_register_symbolic_metadata() -> None:
    _load_skyfield_atoms()

    expected = {
        "compute_spherical_coordinate_rates",
        "calculate_vector_angle",
    }
    for name in expected:
        symbolic = REGISTRY[name]["symbolic"]
        assert symbolic is not None, name
        assert symbolic.check_dimensional_consistency() == []
        assert symbolic.bibliography == ["skyfield2019ascl", "repo_skyfield"]


def test_spherical_rates_dimensions_and_bounds_are_registered() -> None:
    _load_skyfield_atoms()

    length = DimensionalSignature(L=1)
    velocity = DimensionalSignature(L=1, T=-1)
    angular_rate = DimensionalSignature(T=-1)
    entry = REGISTRY["compute_spherical_coordinate_rates"]

    assert entry["dim_signature"]["r"] == length
    assert entry["dim_signature"]["v"] == velocity
    assert entry["dim_signature"]["range"] == length
    assert entry["dim_signature"]["latitude"] == DIMENSIONLESS
    assert entry["dim_signature"]["longitude"] == DIMENSIONLESS
    assert entry["dim_signature"]["range_rate"] == velocity
    assert entry["dim_signature"]["latitude_rate"] == angular_rate
    assert entry["dim_signature"]["longitude_rate"] == angular_rate
    assert entry["symbolic"].validity_bounds["range"] == (0.0, None)


def test_vector_angle_dimensions_bounds_and_expression_are_registered() -> None:
    _load_skyfield_atoms()

    length = DimensionalSignature(L=1)
    entry = REGISTRY["calculate_vector_angle"]
    symbolic = entry["symbolic"]

    assert entry["dim_signature"]["u"] == length
    assert entry["dim_signature"]["v"] == length
    assert entry["dim_signature"]["theta"] == DIMENSIONLESS
    assert symbolic.validity_bounds["theta"][0] == 0.0
    assert symbolic.validity_bounds["theta"][1] > 3.0
    assert symbolic.validity_bounds["u_norm"] == (0.0, None)
    assert symbolic.validity_bounds["w_norm"] == (0.0, None)

    equation = symbolic.to_sympy()
    theta, ux, uy, uz, wx, wy, wz, u_norm, w_norm = sp.symbols(
        "theta ux uy uz wx wy wz u_norm w_norm"
    )
    assert equation.lhs == sp.cos(theta)
    expected_rhs = (ux * wx + uy * wy + uz * wz) / (u_norm * w_norm)
    assert sp.simplify(equation.rhs - expected_rhs) == 0

