"""Explicitly bounded next-cylinder geometry with a required validity mask."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_next_cylinder_intersection(x0: AbstractArray, y0: AbstractArray, z0: AbstractArray,
    hel_xm: AbstractArray, hel_ym: AbstractArray, hel_r: AbstractArray, hel_pitch: AbstractArray,
    sign_uz: AbstractArray, target_r2sqr: AbstractArray) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    arrays = [x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, sign_uz, target_r2sqr]
    if len(x0.shape) != 1 or any(a.shape != x0.shape for a in arrays):
        raise ValueError('Identical one-dimensional shapes required')
    return (*[AbstractArray(shape=x0.shape, dtype='float64') for _ in range(4)], AbstractArray(shape=x0.shape, dtype='bool'))


@register_atom(witness_next_cylinder_intersection)
def next_cylinder_intersection(x0: NDArray[np.float64], y0: NDArray[np.float64], z0: NDArray[np.float64],
    hel_xm: NDArray[np.float64], hel_ym: NDArray[np.float64], hel_r: NDArray[np.float64], hel_pitch: NDArray[np.float64],
    sign_uz: NDArray[np.float64], target_r2sqr: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.bool_]]:
    """Return xi,yi,zi,dphi,valid for the next strictly forward cylinder crossing.

    All inputs must be finite real, identical nonempty shape (N,). Radii and
    target radius squared are positive, pitch is nonzero, sign_uz is +/-1.
    Starting xy must lie on the stated helix circle within relative 1e-10.
    Length units must agree; pitch is z advance per 2*pi. Coaxial circles are
    excluded because they have either no intersection or continuous contact.

    No-intersection rows have valid=False and four zero placeholders, which
    MUST be ignored. Circle reachability is checked before rounding the cosine
    at tangent boundaries; unreachable circles cannot become crossings.
    Both rotational directions use modulo 2*pi;
    an already-contacting root advances to the next turn, never phase zero.
    Positive advances below 1e-6 radians are skipped until their next turn.
    Inputs are not mutated. This is surface geometry, not full track finding.
    """
    arrays = []
    for value in (x0, y0, z0, hel_xm, hel_ym, hel_r, hel_pitch, sign_uz, target_r2sqr):
        raw = np.asarray(value)
        if raw.dtype.kind not in 'iuf' or raw.ndim != 1 or not raw.size:
            raise ValueError('Nonempty real one-dimensional inputs required')
        with np.errstate(over='raise', invalid='raise'):
            a = raw.astype(np.float64)
        if not np.all(np.isfinite(a)):
            raise ValueError('Finite inputs required')
        arrays.append(a)
    x, y, z, cx, cy, radius, pitch, zsign, target2 = arrays
    if any(a.shape != x.shape for a in arrays):
        raise ValueError('Identical shapes required')
    if np.any(radius <= 0) or np.any(target2 <= 0) or np.any(pitch == 0) or np.any(~np.isin(zsign, [-1., 1.])):
        raise ValueError('Positive radii, nonzero pitch and signed unit direction required')
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        dx, dy = x-cx, y-cy
        rho = np.hypot(cx, cy)
        if np.any(rho == 0):
            raise ValueError('Coaxial geometry is outside this crossing contract')
        if not np.allclose(np.hypot(dx, dy), radius, rtol=1e-10, atol=0):
            raise ValueError('Starting point is not on the stated helix')
        scale = np.maximum.reduce([rho, radius, np.sqrt(target2)])
        a, b, c = rho/scale, radius/scale, np.sqrt(target2)/scale
        cosine = (c*c-a*a-b*b)/(2*a*b)
        valid = np.isfinite(cosine) & (c >= np.abs(a-b)) & (c <= a+b)
        phase0 = np.arctan2(dy, dx)-np.arctan2(cy, cx)
        # Invalid rows are placeholders only and remain masked below.
        angle = np.arccos(np.where(valid, np.clip(cosine, -1., 1.), 0.))
        direction = zsign*np.sign(pitch)
        advance = np.mod(direction[:, None]*(np.stack([angle, -angle], axis=1)-phase0[:, None]), 2*np.pi)
        advance = np.where(advance < 1e-6, advance+2*np.pi, advance)
        phase = direction*np.min(advance, axis=1)
        xi = cx+np.cos(phase)*dx-np.sin(phase)*dy
        yi = cy+np.sin(phase)*dx+np.cos(phase)*dy
        zi = z+phase*pitch/(2*np.pi)
    outputs = tuple(np.where(valid, value, 0.) for value in (xi, yi, zi, phase))
    if any(not np.all(np.isfinite(value)) for value in outputs):
        raise ValueError('Intersection exceeds finite output range')
    return (*outputs, valid)
