"""Auto-generated atom wrappers following the sciona pattern."""

from __future__ import annotations

import numpy as np

import icontract
from sciona.ghost.decorators import symbolic_atom
from .expressions import (
    SKYFIELD_BIBLIOGRAPHY,
    SPHERICAL_RANGE_RATE_EXPR,
    SPHERICAL_RATES_DIM_MAP,
    SPHERICAL_RATES_VALIDITY_BOUNDS,
    SPHERICAL_RATES_VARIABLES,
    VECTOR_ANGLE_DIM_MAP,
    VECTOR_ANGLE_EXPR,
    VECTOR_ANGLE_VALIDITY_BOUNDS,
    VECTOR_ANGLE_VARIABLES,
)
from .witnesses import (
    witness_compute_spherical_coordinate_rates,
    witness_calculate_vector_angle,
)
from skyfield.functions import angle_between
from skyfield.functions import _to_spherical_and_rates


@symbolic_atom(
    witness_compute_spherical_coordinate_rates,
    expr=SPHERICAL_RANGE_RATE_EXPR,
    dim_map=SPHERICAL_RATES_DIM_MAP,
    validity_bounds=SPHERICAL_RATES_VALIDITY_BOUNDS,
    variables=SPHERICAL_RATES_VARIABLES,
    bibliography=SKYFIELD_BIBLIOGRAPHY,
)
@icontract.require(lambda r: r is not None, "r cannot be None")
@icontract.require(lambda v: v is not None, "v cannot be None")
@icontract.ensure(lambda result: result is not None, "compute_spherical_coordinate_rates output must not be None")
def compute_spherical_coordinate_rates(
    r: np.ndarray,
    v: np.ndarray,
) -> tuple[float, float, float, float, float, float]:
    """Computes spherical coordinates and their instantaneous rates.

    Args:
        r: Cartesian position vector(s).
        v: Cartesian velocity vector(s).

    Returns:
        A 6-tuple of `(range, latitude, longitude, range_rate, latitude_rate, longitude_rate)`.
    """
    return _to_spherical_and_rates(r, v)

@symbolic_atom(
    witness_calculate_vector_angle,
    expr=VECTOR_ANGLE_EXPR,
    dim_map=VECTOR_ANGLE_DIM_MAP,
    validity_bounds=VECTOR_ANGLE_VALIDITY_BOUNDS,
    variables=VECTOR_ANGLE_VARIABLES,
    bibliography=SKYFIELD_BIBLIOGRAPHY,
)
@icontract.require(lambda u: u is not None, "u cannot be None")
@icontract.require(lambda v: v is not None, "v cannot be None")
@icontract.ensure(lambda result: result is not None, "calculate_vector_angle output must not be None")
def calculate_vector_angle(u: np.ndarray, v: np.ndarray) -> float:
    """Computes the angle between two vectors.

    Args:
        u: First vector.
        v: Second vector.

    Returns:
        The angle in radians.
    """
    return angle_between(u, v)
