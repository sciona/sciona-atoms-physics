"""Circular-path circumference and average speed from radius and period."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_circular_orbit_speed(radius: AbstractArray, period: AbstractArray) -> tuple[AbstractArray,AbstractArray]:
    if radius.shape!=period.shape:raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=radius.shape,dtype='float64') for _ in range(2))


@register_atom(witness_circular_orbit_speed)
def circular_orbit_speed(radius: NDArray[np.float64], period: NDArray[np.float64]
                         ) -> tuple[NDArray[np.float64],NDArray[np.float64]]:
    """Return circumference2*pi*r (m) and average speed2*pi*r/T (m/s).

    Inputs positive finite radius in metres and period in seconds; identical
    nonempty real float64-compatible shapes including scalar arrays. No
    broadcasting; inputs preserved. Circular-path average speed is instantaneous
    speed only for uniform circular motion. No gravitational dynamics, eccentric
    orbit, direction or ephemeris claim. The caller establishes the circular-path
    approximation and consistent units. No calendar year conversion is implicit.

    Both outputs computed independently at450 decimal digits in invocation-local
    mpmath context before float64 rounding. Both must be positive finite
    representable; subnormals accepted, nonzero underflow and overflow rejected.
    No reuse of rounded circumference for speed. Accuracy tests are not a
    universal correctly-rounded proof for pi-dependent outputs. Requires precision
    extra; no throughput claim.
    """
    import mpmath
    arrays=[]
    for value in [radius,period]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('Positive finite inputs required')
        arrays.append(a)
    if arrays[0].shape!=arrays[1].shape:raise ValueError('Identical shapes required without broadcasting')
    ctx=mpmath.mp.clone();ctx.dps=450
    outputs=[[],[]]
    for r,t in zip(arrays[0].flat,arrays[1].flat):
        mr,mt=ctx.mpf(float(r)),ctx.mpf(float(t))
        values=[2*ctx.pi*mr,2*ctx.pi*mr/mt]
        for bucket,value in zip(outputs,values):
            rounded=float(value)
            if not np.isfinite(rounded) or rounded<=0:raise ValueError('Output outside positive float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
