"""Two ideal parallel resistors with signed common voltage."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_parallel_resistance(resistance_1: AbstractArray, resistance_2: AbstractArray, voltage: AbstractArray
                                ) -> tuple[AbstractArray,AbstractArray,AbstractArray,AbstractArray]:
    if resistance_1.shape!=resistance_2.shape or resistance_1.shape!=voltage.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=resistance_1.shape,dtype='float64') for _ in range(4))


@register_atom(witness_parallel_resistance)
def parallel_resistance(resistance_1: NDArray[np.float64], resistance_2: NDArray[np.float64], voltage: NDArray[np.float64]
                        ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return equivalent resistance (ohms), branch currents and total current (A).

    R1,R2 are positive finite ideal linear resistances across the same two nodes;
    V is finite signed common voltage with consistently oriented branch currents.
    Inputs identical nonempty real float64-compatible shapes, including scalars.
    No broadcasting. Req=R1*R2/(R1+R2), I1=V/R1, I2=V/R2, It=I1+I2.
    Zero voltage gives zero currents; Req follows the constitutive model, not0/0.
    Caller establishes network topology and units. No ideal short/open circuit,
    negative resistance, reactive impedance or nonlinear-device claim.

    Exact rational arithmetic on converted binary64 inputs precedes independent
    output rounding. No reuse of rounded resistance or branch currents. Outputs
    must all be finite representable; exact zeros and subnormals accepted, nonzero
    underflow/overflow rejected. Input arrays preserved. No throughput claim.
    """
    arrays=[]
    for value in [resistance_1,resistance_2,voltage]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all():raise ValueError('Finite inputs required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays):raise ValueError('Identical shapes required')
    if any(np.any(a<=0) for a in arrays[:2]):raise ValueError('Positive resistances required')
    outputs=[[],[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        r1,r2,v=map(lambda x:Fraction(float(x)),row)
        i1,i2=v/r1,v/r2
        for bucket,value in zip(outputs,[r1*r2/(r1+r2),i1,i2,i1+i2]):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Circuit output outside float64 range') from error
            if not np.isfinite(rounded) or (value and rounded==0):raise ValueError('Nonzero output outside representable float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
