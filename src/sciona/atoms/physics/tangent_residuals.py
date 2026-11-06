"""Reusable residual projections and independent uncertainty combination.

Projection arithmetic adapted from edwinst/trackml_solution (BSD-2-Clause).
Copyright and license: ../particle_tracking/source_tracking/solution_LICENSE.source.
No detector topology or fitted calibration coefficients are embedded.
"""
import numpy as np
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete finite numeric inputs required')


def _array(value, dimensions):
    result = np.asarray(value)
    if result.dtype != np.float64 or result.ndim != dimensions or not np.isfinite(result).all():
        raise ValueError('Finite float64 array with the declared rank required')
    return result


@register_atom(concrete_only)
def hemisphere_tangent_displacement(points: np.ndarray, reference: np.ndarray
                                    ) -> tuple[np.ndarray, np.ndarray]:
    """Project point-minus-reference displacement onto hemisphere tangent axes.

Both arrays have shape (N,3), share an origin and caller-defined length unit.
The polar basis is sign(z) times the conventional increasing-colatitude basis;
at z=0 it is the zero vector. The azimuthal basis points toward increasing
azimuth. Outputs are signed lengths, not angles. Rotation-axis points reject.
Empty batches are allowed. Source arithmetic order is preserved; nonfinite
intermediates/results reject rather than representing a valid projection.
"""
    p, q = _array(points, 2), _array(reference, 2)
    if p.shape != q.shape or p.shape[1] != 3:
        raise ValueError('Aligned (N,3) coordinates required')
    x, y, z = p.T
    with np.errstate(over='ignore', divide='ignore', invalid='ignore', under='ignore'):
        rho = np.sqrt(np.square(x) + np.square(y))
        radius = np.sqrt(np.square(x) + np.square(y) + np.square(z))
        denominator = rho * radius
        if np.any(denominator == 0) or not np.isfinite(denominator).all():
            raise ValueError('Finite nonzero radial normalization required')
        factor = np.abs(z) / denominator
        tx, ty, tz = factor*x, factor*y, -np.sign(z)*rho/radius
        ax, ay = -y/rho, x/rho
        dx, dy, dz = (p-q).T
        polar = tx*dx + ty*dy + tz*dz
        azimuth = ax*dx + ay*dy + 0*dz
    if not all(np.isfinite(a).all() for a in (tx, ty, tz, ax, ay, dx, dy, dz, polar, azimuth)):
        raise ValueError('Finite tangent arithmetic required')
    return polar, azimuth


@register_atom(concrete_only)
def combine_scaled_uncertainty(measured: np.ndarray, driver: np.ndarray,
                               driver_scale: float, component_scale: float) -> np.ndarray:
    """Combine independent measured and scaled-driver uncertainty in quadrature.

Aligned float64 vectors (N,); measured is nonnegative, driver may be signed.
Compute sqrt(measured**2 + ((driver*driver_scale)*component_scale)**2).
Coefficients are explicit finite nonnegative scalars. Their product converts
driver units to measured units; no empirical coefficients or independence
inference are supplied. Zero and empty inputs are allowed. Overflow rejects;
this preserves multiplication order rather than using an overflow-safe hypot.
"""
    m, d = _array(measured, 1), _array(driver, 1)
    if m.shape != d.shape or np.any(m < 0):
        raise ValueError('Aligned vectors and nonnegative measured uncertainty required')
    for value in (driver_scale, component_scale):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.floating)) or not np.isfinite(value) or value < 0:
            raise ValueError('Finite nonnegative real scalar coefficients required')
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        prediction = d * driver_scale
        component = prediction * component_scale
        result = np.sqrt(np.square(m) + np.square(component))
    if not all(np.isfinite(a).all() for a in (prediction, component, result)):
        raise ValueError('Finite uncertainty arithmetic required')
    return result
