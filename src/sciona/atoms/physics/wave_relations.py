"""Positive-frequency periodic-wave parameters with explicit angular conventions."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_wave_relations(frequency: AbstractArray, phase_speed: AbstractArray
                          ) -> tuple[AbstractArray,AbstractArray,AbstractArray,AbstractArray]:
    if frequency.shape!=phase_speed.shape:raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=frequency.shape,dtype='float64') for _ in range(4))


@register_atom(witness_wave_relations)
def wave_relations(frequency: NDArray[np.float64], phase_speed: NDArray[np.float64]
                   ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return period, wavelength, angular frequency and angular wavenumber.

    Inputs are finite positive ordinary frequency in cycles/s and phase-speed
    magnitude in m/s, with identical nonempty shapes including scalar arrays.
    Float64 conversion, no broadcasting. Outputs T=1/f (s), lambda=v/f (m),
    omega=2*pi*f (rad/s), k=2*pi*f/v (rad/m) have the input shape.

    Caller establishes a single periodic mode and its phase speed, which need
    not equal group velocity. These are magnitudes, not a signed wavevector,
    spatial cycles per length, dispersion inference or broadband estimation.
    Inputs are preserved. Every output must be positive finite representable
    float64; subnormals are accepted, nonzero underflow to zero and overflow
    rejected. No output is derived from an already-rounded output.

    Rational outputs use exact arithmetic on converted binary64 values. Angular
    outputs use an invocation-local mpmath context at 450 decimal digits before
    rounding. Retained accuracy evidence is not a universal correctly-rounded
    proof for pi-dependent outputs. Requires precision extra; no throughput claim.
    """
    import mpmath
    arrays=[]
    for value in [frequency,phase_speed]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):
            a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('Positive finite inputs required')
        arrays.append(a)
    if arrays[0].shape!=arrays[1].shape:raise ValueError('Identical shapes required without broadcasting')
    ctx=mpmath.mp.clone();ctx.dps=450
    outputs=[[],[],[],[]]
    for f,v in zip(arrays[0].flat,arrays[1].flat):
        rf,rv=Fraction(float(f)),Fraction(float(v))
        mf,mv=ctx.mpf(float(f)),ctx.mpf(float(v))
        values=[1/rf,rv/rf,2*ctx.pi*mf,2*ctx.pi*mf/mv]
        for bucket,value in zip(outputs,values):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Wave parameter outside float64 range') from error
            if not np.isfinite(rounded) or rounded<=0:raise ValueError('Wave parameter outside positive float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
