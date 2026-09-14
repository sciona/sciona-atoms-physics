"""Circular test-mass orbital radius from period."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_orbit_radius(gravitational_constant: AbstractArray, central_mass: AbstractArray,
                         period: AbstractArray) -> tuple[AbstractArray,AbstractArray]:
    if gravitational_constant.shape!=central_mass.shape or central_mass.shape!=period.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=period.shape,dtype='float64') for _ in range(2))


@register_atom(witness_orbit_radius)
def orbit_radius(gravitational_constant: NDArray[np.float64], central_mass: NDArray[np.float64],
                 period: NDArray[np.float64]) -> tuple[NDArray[np.float64],NDArray[np.float64]]:
    """Return center-based radius (m) and circular orbital speed (m/s).

    Positive finite G (m^3 kg^-1 s^-2), central mass (kg), and period (s), with
    identical nonempty real float64-compatible shapes; scalars allowed, no
    broadcasting. Newtonian uniform circular test-mass orbit, exterior spherical
    central field, gravity the sole centripetal force. Satellite mass negligible
    compared to central mass. Radius is not altitude; caller establishes exterior
    clearance. No finite-mass two-body, oblateness or station-keeping correction.
    Geostationary interpretation additionally requires equatorial prograde
    circular motion at the sidereal rotation period; period alone cannot certify
    it. No hardcoded Earth constants or solar/sidereal day conversion.

    Local450digit mpmath evaluates r=cbrt(G*M*T^2/(4*pi^2)) and v=2*pi*r/T before
    independent float64 rounding. Input copies converted to float64 first.
    Avoids intermediate float64 product overflow/underflow. Positive subnormals
    accepted, nonzero underflow to zero or overflow rejects the entire call.
    Reference tests are not a universal correct-rounding proof. Precision extra
    required; no throughput claim.
    """
    import mpmath
    arrays=[]
    for value in (gravitational_constant,central_mass,period):
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):arr=raw.astype(np.float64,copy=True)
        if not np.isfinite(arr).all() or np.any(arr<=0):raise ValueError('Positive finite inputs required')
        arrays.append(arr)
    if any(a.shape!=arrays[0].shape for a in arrays[1:]):raise ValueError('Identical shapes required without broadcasting')
    ctx=mpmath.mp.clone();ctx.dps=450
    outputs=[[],[]]
    for row in zip(*(a.flat for a in arrays)):
        G,M,T=(ctx.mpf(float(v)) for v in row)
        radius=ctx.root(G*M*T*T/(4*ctx.pi**2),3)
        speed=2*ctx.pi*radius/T
        for bucket,value in zip(outputs,(radius,speed)):
            rounded=float(value)
            if not np.isfinite(rounded) or rounded<=0:raise ValueError('Output outside positive float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
