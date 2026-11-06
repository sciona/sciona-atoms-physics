"""Helix intersection with an explicit coaxial cylinder and movement bound.

Arithmetic adapted from edwinst/trackml_solution geometry.py (BSD-2-Clause).
Copyright and license: ../particle_tracking/source_tracking/solution_LICENSE.source.
Layer selection, finite cylinder extent, corrections and retries are caller policy.
"""
import numpy as np
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete finite helix arrays required')


@register_atom(concrete_only)
def helix_cylinder_intersection(
    x0: np.ndarray, y0: np.ndarray, z0: np.ndarray,
    center_x: np.ndarray, center_y: np.ndarray, radius: np.ndarray,
    pitch: np.ndarray, axial_direction: np.ndarray,
    target_radius_squared: np.ndarray, minimum_phase: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return x,y,z,phase,hit for each requested cylinder intersection.

All inputs are aligned finite float64 vectors, including empty vectors. Lengths
share caller-defined units; pitch is axial advance per revolution. Direction
uses its sign only. Radius and target radius squared must be positive; pitch,
direction and transverse center magnitude must be nonzero. Initial points are
assumed to lie on the specified helix; this relationship is caller responsibility.
Minimum phase is a signed dimensionless movement bound, allowing backward
reselection. Four source candidate phases are considered, not an unbounded
multi-revolution search. Geometric misses return NaN coordinates/phase and
false hit flags. Undefined or nonfinite intermediate arithmetic raises.
"""
    values = [np.asarray(v) for v in (x0, y0, z0, center_x, center_y, radius,
              pitch, axial_direction, target_radius_squared, minimum_phase)]
    if any(v.dtype != np.float64 or v.ndim != 1 or v.shape != values[0].shape
           or not np.isfinite(v).all() for v in values):
        raise ValueError('Aligned finite float64 vectors required')
    x0, y0, z0, center_x, center_y, radius, pitch, axial_direction, target_radius_squared, minimum_phase = values
    if (np.any(radius <= 0) or np.any(target_radius_squared <= 0)
            or np.any(pitch == 0) or np.any(axial_direction == 0)):
        raise ValueError('Positive radii and nonzero pitch/direction required')
    with np.errstate(over='ignore', invalid='ignore', divide='ignore', under='ignore'):
        dx, dy = x0-center_x, y0-center_y
        phi0 = np.arctan2(dy, dx)
        center_radius = np.sqrt(np.square(center_x)+np.square(center_y))
        phase0 = phi0-np.arctan2(center_y, center_x)
        phase0[phase0 < 0] += 2*np.pi
        phase0[phase0 >= 2*np.pi] -= 2*np.pi
        maximum = np.square(center_radius+radius)
        minimum = np.square(center_radius-radius)
        base = np.square(center_radius)+np.square(radius)
        denominator = 2*center_radius*radius
        if (np.any(denominator == 0) or any(not np.isfinite(v).all()
                for v in (dx, dy, center_radius, maximum, minimum, base, denominator))):
            raise ValueError('Undefined or nonfinite cylinder geometry')
        hit = (target_radius_squared <= maximum) & (target_radius_squared >= minimum)
        cosine = (target_radius_squared-base)/denominator
        cosine[~hit] = 0.
        angle = np.arccos(cosine)
        # Multiplying finite pitch and direction can overflow; only signs matter.
        direction = np.sign(axial_direction)*np.sign(pitch)
        candidates = np.zeros((x0.size, 4))
        candidates[:, 0] = angle-phase0
        candidates[:, 1] = -angle-phase0
        candidates[:, 2] = candidates[:, 0]+2*np.pi
        candidates[:, 3] = candidates[:, 1]+2*np.pi
        candidates *= direction[:, None]
        candidates[candidates < minimum_phase[:, None]] = np.inf
        phase = direction*np.amin(candidates, axis=1)
        hit[np.isinf(phase)] = False
        phase[~hit] = 0.
        axial_step = pitch/(2*np.pi)
        cosine_phase, sine_phase = np.cos(phase), np.sin(phase)
        x = center_x+cosine_phase*dx-sine_phase*dy
        y = center_y+sine_phase*dx+cosine_phase*dy
        z = z0+phase*axial_step
    if any(not np.isfinite(v).all() for v in (x, y, z, phase)):
        raise ValueError('Nonfinite intersection arithmetic')
    for value in (x, y, z, phase):
        value[~hit] = np.nan
    return x, y, z, phase, hit
