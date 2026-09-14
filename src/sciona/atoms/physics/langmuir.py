"""Single-species Langmuir equilibrium with independent vacancy evaluation."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_langmuir(adsorption_coefficient: AbstractArray, desorption_coefficient: AbstractArray,
                     pressure: AbstractArray, total_sites: AbstractArray
                     ) -> tuple[AbstractArray,AbstractArray,AbstractArray,AbstractArray]:
    if any(a.shape!=pressure.shape for a in (adsorption_coefficient,desorption_coefficient,total_sites)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=pressure.shape,dtype='float64') for _ in range(4))


@register_atom(witness_langmuir)
def langmuir(adsorption_coefficient: NDArray[np.float64], desorption_coefficient: NDArray[np.float64],
             pressure: NDArray[np.float64], total_sites: NDArray[np.float64]
             ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return coverage, occupied site density, vacant site density, equilibrium rate.

    Positive ka in Pa^-1 s^-1, positive kd in s^-1, nonnegative partial pressure
    p in Pa, positive total site density N in m^-2. Identical nonempty real
    float64-compatible shapes including scalars; no broadcasting. Fixed
    temperature, single non-dissociative adsorbate, identical independent sites,
    at most one molecule per site; no lateral interactions or multilayers.
    K=ka/kd is inverse pressure. No transient, competitive or material-fit claim.

    With q=ka*p and d=kd+q, outputs are q/d, N*q/d, N*kd/d and N*q*kd/d.
    The rate is the common adsorption/desorption event rate per area, not net
    accumulation (which is zero at equilibrium). At p=0 coverage, occupancy and
    rate are exactly zero and vacancy is N, established directly by rate/site
    balance without the source reciprocal steps. Caller supplies applicable
    coefficients at the temperature of interest.

    Inputs copied and converted to float64, then exact rational arithmetic on
    those values, independently rounded once per output. No intermediate product
    overflow or subtraction of rounded occupancy. Near saturation coverage may
    round to1 while a positive vacancy is retained; use returned vacancy instead
    of N*(1-coverage). Exact zeros/subnormals allowed. Nonzero underflow or
    overflow in any output rejects the call. No throughput claim.
    """
    arrays=[]
    for i,value in enumerate((adsorption_coefficient,desorption_coefficient,pressure,total_sites)):
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<0 if i==2 else a<=0):
            raise ValueError('Nonnegative pressure and positive finite coefficients/site density required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays[1:]):raise ValueError('Identical shapes required without broadcasting')
    outputs=[[],[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        ka,kd,p,N=(Fraction(float(v)) for v in row)
        q=ka*p;den=kd+q
        values=(q/den,N*q/den,N*kd/den,N*q*kd/den)
        for bucket,value in zip(outputs,values):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Output overflow') from error
            if not np.isfinite(rounded) or (value!=0 and rounded==0):raise ValueError('Output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
