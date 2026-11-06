"""Reusable radial coordinate projections with explicit reference geometry.

Arithmetic adapted from edwinst/trackml_solution neighbors.py (BSD-2-Clause).
Copyright and license: ../particle_tracking/source_tracking/solution_LICENSE.source.
No detector layout, identifiers or neighbor-selection policy are embedded.
"""
import numpy as np
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete finite coordinates and projection parameters required')


def _coordinates(coords):
    value = np.asarray(coords)
    if value.dtype != np.float64 or value.ndim != 2 or value.shape[1] != 3 or not np.isfinite(value).all():
        raise ValueError('Finite float64 coordinates of shape (N, 3) required')
    return value


def _scalar(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.floating)) or not np.isfinite(value):
        raise ValueError('Finite real scalar required')
    return value


@register_atom(concrete_only)
def cylindrical_projection(coords: np.ndarray, reference_radius: float,
                           transverse_weight: float = 1.0) -> np.ndarray:
    """Project rays to a cylinder, then weight transverse coordinates.

Coordinates and reference_radius use the same caller-defined length unit;
transverse_weight is dimensionless. Axis points and nonfinite arithmetic
reject. Empty batches return shape (0, 3). Multiplication precedes division
to preserve the retained source's floating-point evaluation order.
"""
    points = _coordinates(coords)
    radius, weight = _scalar(reference_radius), _scalar(transverse_weight)
    if radius <= 0:
        raise ValueError('Positive reference radius required')
    with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
        radial = np.linalg.norm(points[:, :2], axis=1)
        if np.any(radial == 0) or not np.isfinite(radial).all():
            raise ValueError('Finite nonzero radial magnitude required')
        projected = points * radius / radial[:, np.newaxis]
        result = projected.copy()
        result[:, :2] = result[:, :2] * weight
    if not np.isfinite(result).all():
        raise ValueError('Projection has no finite result')
    return result


@register_atom(concrete_only)
def plane_projection(coords: np.ndarray, reference_height: float) -> np.ndarray:
    """Project rays from the origin onto z=reference_height; return x,y.

Coordinates and reference_height use the same caller-defined length unit.
Points on z=0 reject; negative heights and empty batches are supported.
"""
    points = _coordinates(coords)
    height = _scalar(reference_height)
    if np.any(points[:, 2] == 0):
        raise ValueError('Nonzero axial coordinate required')
    with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
        result = points[:, :2] * (height / points[:, 2])[:, np.newaxis]
    if not np.isfinite(result).all():
        raise ValueError('Projection has no finite result')
    return result
