"""Reusable rectilinear linear interpolation with explicit extrapolation."""
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete grid arrays and interpolation state required')


@register_atom(concrete_only)
def fit_linear_grid(axes: object, values: np.ndarray) -> object:
    """Build a copied linear interpolator on a rectilinear grid.

Axes is a nonempty tuple/list of finite float64 vectors, each at least length
two and strictly ascending or descending. Values is finite float64, with
leading dimensions matching axis lengths and optional trailing component
dimensions. Caller defines axis units and component units. No sorting,
singleton removal, coordinate conversion or domain policy is performed.
The opaque runtime state must not be modified; it is not a portable artifact.
Queries extrapolate linearly outside the grid without a physical validity claim.
"""
    if not isinstance(axes, (tuple, list)) or not axes:
        raise ValueError('Nonempty sequence of grid axes required')
    copied = []
    for axis in axes:
        a = np.asarray(axis)
        if a.dtype != np.float64 or a.ndim != 1 or a.size < 2 or not np.isfinite(a).all():
            raise ValueError('Finite float64 axis with at least two entries required')
        if not (np.all(a[1:] > a[:-1]) or np.all(a[1:] < a[:-1])):
            raise ValueError('Strictly monotonic axis required')
        copied.append(a.copy())
    v = np.asarray(values)
    if (v.dtype != np.float64 or v.ndim < len(copied) or not np.isfinite(v).all()
            or v.shape[:len(copied)] != tuple(len(a) for a in copied)):
        raise ValueError('Finite float64 values matching grid dimensions required')
    return RegularGridInterpolator(tuple(copied), v.copy(), method='linear',
                                   bounds_error=False, fill_value=None)


@register_atom(concrete_only)
def evaluate_linear_grid(points: np.ndarray, state: object) -> np.ndarray:
    """Evaluate copied linear grid state at finite float64 points (Q,D).

Returns shape (Q,) plus any trailing value component dimensions. Q=0 is
supported. Axis order and units must match the fitted grid. Extrapolation is
enabled; nonfinite arithmetic results reject. No interpolation error bound or
cross-version bitwise guarantee is supplied. State must remain unmodified.
"""
    if (not isinstance(state, RegularGridInterpolator) or state.method != 'linear'
            or state.bounds_error is not False or state.fill_value is not None):
        raise ValueError('Unmodified linear extrapolating grid state required')
    p = np.asarray(points)
    if (p.dtype != np.float64 or p.ndim != 2 or p.shape[1] != len(state.grid)
            or not np.isfinite(p).all()):
        raise ValueError('Finite float64 query matrix matching grid dimension required')
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        result = state(p)
    if not np.isfinite(result).all():
        raise ValueError('Interpolation produced nonfinite values')
    return result
