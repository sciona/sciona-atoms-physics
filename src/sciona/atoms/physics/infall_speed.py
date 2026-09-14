"""Radial infall from rest at infinity in a fixed Newtonian central field."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_infall_speed(gravitational_constant: AbstractArray, test_mass: AbstractArray,
                        central_mass: AbstractArray, radius: AbstractArray) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    if any(a.shape != radius.shape for a in (gravitational_constant, test_mass, central_mass)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=radius.shape, dtype='float64') for _ in range(4))


@register_atom(witness_infall_speed)
def infall_speed(gravitational_constant: NDArray[np.float64], test_mass: NDArray[np.float64],
                 central_mass: NDArray[np.float64], radius: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return speed, inward_radial_velocity, gravitational_work, potential_energy.

    Positive finite G (SI), test mass (kg), fixed central mass (kg), and positive
    center-based radius (m), with equal nonempty real float64-compatible shapes.
    Scalars accepted; no broadcasting. The caller establishes a negligible test
    mass and an exterior spherical/point-source field. No finite-mass two-body,
    drag, relativity, body clearance or finite travel-time claim. Rest at infinity
    is an asymptotic zero-energy condition. Speed sqrt(2GM/r) is positive; radial
    velocity is negative; gravitational work GMm/r is positive and potential is
    its negative with zero at infinity. Speed also equals ideal escape threshold
    magnitude, not a guarantee of a collision-free escape trajectory.

    Inputs copied to float64. Local450digit arithmetic before independently
    rounding all outputs avoids intermediate float64 overflow/underflow.
    Subnormals accepted; nonzero output underflow or overflow rejects the call.
    Finite tests are not a universal correct-rounding proof.
    """
    import mpmath
    arrays = []
    for value in (gravitational_constant, test_mass, central_mass, radius):
        raw = np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            arr = raw.astype(np.float64, copy=True)
        if not np.isfinite(arr).all() or np.any(arr <= 0):
            raise ValueError('Positive finite inputs required')
        arrays.append(arr)
    if any(a.shape != arrays[0].shape for a in arrays[1:]):
        raise ValueError('Identical shapes required without broadcasting')
    ctx = mpmath.mp.clone()
    ctx.dps = 450
    outputs = [[], [], [], []]
    for row in zip(*(a.flat for a in arrays)):
        G, m, M, r = (ctx.mpf(float(x)) for x in row)
        speed = ctx.sqrt(2*G*M/r)
        work = G*m*M/r
        for bucket, value in zip(outputs, (speed, -speed, work, -work)):
            rounded = float(value)
            if not np.isfinite(rounded) or rounded == 0:
                raise ValueError('Output outside nonzero float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
