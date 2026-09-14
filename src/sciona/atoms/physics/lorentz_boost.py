"""Standard inertial x-axis Lorentz boost with cancellation-safe intermediates."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_lorentz_boost(light_speed: AbstractArray, relative_velocity: AbstractArray,
                         time: AbstractArray, x: AbstractArray, y: AbstractArray, z: AbstractArray
                         ) -> tuple[AbstractArray,AbstractArray,AbstractArray,AbstractArray,AbstractArray]:
    if any(a.shape!=time.shape for a in (light_speed,relative_velocity,x,y,z)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=time.shape,dtype='float64') for _ in range(5))


@register_atom(witness_lorentz_boost)
def lorentz_boost(light_speed: NDArray[np.float64], relative_velocity: NDArray[np.float64],
                  time: NDArray[np.float64], x: NDArray[np.float64], y: NDArray[np.float64], z: NDArray[np.float64]
                  ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return gamma,time_prime,x_prime,y_prime,z_prime for a standard x boost.

    Positive finite c (m/s), signed finite v with |v|<c; event time seconds and
    signed spatial coordinates meters. Equal nonempty real float64-compatible
    shapes, scalar arrays allowed, no broadcasting. Frame S-prime moves at v
    along S's x-axis, with aligned axes and origins coincident at t=t-prime=0.
    t-prime=gamma*(t-v*x/c²), x-prime=gamma*(x-v*t); y,z unchanged.
    Gamma is positive. v=0 returns identity. No accelerated/curved-spacetime,
    arbitrary-axis, superluminal or coordinate-unit inference claim.

    Inputs copied to float64. Exact rational subtraction forms c²-v² and both
    coordinate numerators before a local450digit square root/multiplication.
    Independent float64 output rounding accepts exact zeros and subnormals;
    nonzero underflow and overflow reject the call. Interval preservation and
    inverse identities are exact model statements, not exact identities between
    independently rounded outputs. No universal correct-rounding/throughput claim.
    """
    import mpmath
    arrays=[]
    for value in (light_speed,relative_velocity,time,x,y,z):
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):arr=raw.astype(np.float64,copy=True)
        if not np.isfinite(arr).all():raise ValueError('Finite inputs required')
        arrays.append(arr)
    if any(a.shape!=arrays[0].shape for a in arrays[1:]):raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[0]<=0) or np.any(np.abs(arrays[1])>=arrays[0]):raise ValueError('Positive c and |v|<c required')
    ctx=mpmath.mp.clone();ctx.dps=450
    convert=lambda q:ctx.mpf(q.numerator)/ctx.mpf(q.denominator)
    outputs=[[],[],[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        c,v,t,X,Y,Z=(Fraction(float(value)) for value in row)
        gamma=ctx.sqrt(convert(c*c/(c*c-v*v)))
        values=(gamma,gamma*convert(t-v*X/(c*c)),gamma*convert(X-v*t),convert(Y),convert(Z))
        for bucket,value in zip(outputs,values):
            rounded=float(value)
            if not np.isfinite(rounded) or (value!=0 and rounded==0):raise ValueError('Nonzero output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
