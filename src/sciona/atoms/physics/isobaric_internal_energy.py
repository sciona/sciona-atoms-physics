"""Local isobaric temperature derivative of internal energy."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_isobaric_internal_energy(cv: AbstractArray, internal_pressure: AbstractArray,
                                    volume: AbstractArray, expansion: AbstractArray) -> AbstractArray:
    if any(a.shape!=cv.shape for a in [internal_pressure,volume,expansion]):
        raise ValueError('Identical shapes required')
    return AbstractArray(shape=cv.shape,dtype='float64')


@register_atom(witness_isobaric_internal_energy)
def isobaric_internal_energy(cv: NDArray[np.float64], internal_pressure: NDArray[np.float64],
                             volume: NDArray[np.float64], expansion: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return (partial U/partial T)_p = Cv + pi_T*V*alpha in J/K.

    Inputs are finite real arrays of identical nonempty shape, including scalar
    arrays, converted to float64. Cv=(partial U/partial T)_V in J/K;
    pi_T=(partial U/partial V)_T in Pa; volume V>0 in m³;
    alpha=(1/V)*(partial V/partial T)_p in K^-1. No broadcasting.

    Caller supplies consistent local derivatives of differentiable U(T,V) and
    V(T,p) at the same state and fixed composition/amount. Expansion and internal
    pressure may be signed. This is an internal-energy derivative, not Cp:
    for a simple compressible system Cp also includes p*V*alpha. Mechanical
    pressure p is distinct from internal pressure pi_T. No stability, material
    equation-of-state inference or finite-temperature-change integration claim.

    Exact rational arithmetic on converted binary64 values precedes one float64
    rounding. Exact zero/subnormal results accepted; nonzero underflow to zero
    and overflow rejected. Inputs remain unchanged.
    """
    arrays=[]
    for value in [cv,internal_pressure,volume,expansion]:
        raw=np.asarray(value)
        if raw.dtype.kind not in 'iuf' or not raw.size:
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):
            a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all():raise ValueError('Finite float64 inputs required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays):raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[2]<=0):raise ValueError('Positive volume required')
    outputs=[]
    for row in zip(*(a.flat for a in arrays)):
        capacity,pressure,size,alpha=[Fraction(float(v)) for v in row]
        exact=capacity+pressure*size*alpha
        try:rounded=float(exact)
        except OverflowError as error:raise ValueError('Derivative exceeds finite float64 range') from error
        if not np.isfinite(rounded) or (exact and rounded==0):raise ValueError('Derivative exceeds representable nonzero float64 range')
        outputs.append(rounded)
    return np.asarray(outputs,dtype=np.float64).reshape(arrays[0].shape)
