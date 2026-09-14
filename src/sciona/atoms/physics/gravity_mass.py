"""Newtonian spherical-source mass from gravitational acceleration."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_gravity_mass(acceleration: AbstractArray, radius: AbstractArray, gravitational_constant: AbstractArray) -> AbstractArray:
    if acceleration.shape!=radius.shape or acceleration.shape!=gravitational_constant.shape:
        raise ValueError('Identical shapes required')
    return AbstractArray(shape=acceleration.shape,dtype='float64')


@register_atom(witness_gravity_mass)
def gravity_mass(acceleration: NDArray[np.float64], radius: NDArray[np.float64], gravitational_constant: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return inferred source mass M=g*r²/G in kilograms.

    Positive finite inputs g in m/s², center distance r in meters and G in
    m³/kg/s², identical nonempty real float64-compatible shapes including scalars.
    No broadcasting. Caller establishes Newtonian spherical symmetry and a
    surface/exterior point. g is pure gravitational acceleration magnitude,
    not effective gravity including rotation. No ephemeris, relativistic or
    nonspherical field inference. G is explicit, not an implicit measured constant.

    Exact rational arithmetic on converted binary64 inputs precedes a single
    output rounding, avoiding intermediate r² or product overflow/underflow.
    Positive finite representable output required; subnormal accepted, underflow
    to zero and overflow rejected. Input arrays preserved. No throughput claim.
    """
    arrays=[]
    for value in [acceleration,radius,gravitational_constant]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('Positive finite inputs required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays):raise ValueError('Identical shapes required')
    outputs=[]
    for row in zip(*(a.flat for a in arrays)):
        g,r,G=map(lambda x:Fraction(float(x)),row)
        try:rounded=float(g*r*r/G)
        except OverflowError as error:raise ValueError('Mass outside float64 range') from error
        if not np.isfinite(rounded) or rounded<=0:raise ValueError('Mass outside positive float64 range')
        outputs.append(rounded)
    return np.asarray(outputs,dtype=np.float64).reshape(arrays[0].shape)
