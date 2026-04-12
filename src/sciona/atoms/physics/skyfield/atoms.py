"""Auto-generated atom wrappers following the ageoa pattern."""

from __future__ import annotations

import numpy as np

import icontract
from ageoa.ghost.registry import register_atom
from .witnesses import (
    witness_compute_spherical_coordinate_rates,
    witness_calculate_vector_angle,
)
from skyfield.functions import angle_between
from skyfield.functions import _to_spherical_and_rates


@register_atom(witness_compute_spherical_coordinate_rates)
@icontract.require(lambda r: r is not None, "r cannot be None")
@icontract.require(lambda v: v is not None, "v cannot be None")
@icontract.ensure(lambda result: result is not None, "compute_spherical_coordinate_rates output must not be None")
def compute_spherical_coordinate_rates(r: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Computes spherical coordinate rates.

    Args:
        r: Cartesian position vector(s).
        v: Cartesian velocity vector(s).

    Returns:
        A tuple containing the rates of change for range, right ascension, and declination.
    """
    return _to_spherical_and_rates(r, v)

@register_atom(witness_calculate_vector_angle)
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