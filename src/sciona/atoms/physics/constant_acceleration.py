"""Signed constant-acceleration motion with exact converted-input arithmetic."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_constant_acceleration(initial_velocity: AbstractArray, acceleration: AbstractArray,
                                 elapsed_time: AbstractArray) -> tuple[AbstractArray,AbstractArray,AbstractArray]:
    if initial_velocity.shape!=acceleration.shape or acceleration.shape!=elapsed_time.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=elapsed_time.shape,dtype='float64') for _ in range(3))


@register_atom(witness_constant_acceleration)
def constant_acceleration(initial_velocity: NDArray[np.float64], acceleration: NDArray[np.float64],
                          elapsed_time: NDArray[np.float64]) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return final_velocity, displacement and average_velocity in SI units.

    Signed initial velocity and constant acceleration, nonnegative elapsed time.
    Finite real float64-compatible nonempty equal-shaped arrays; scalars allowed,
    no broadcasting. One-dimensional signed displacement, not path length.
    Reversal, zero acceleration and zero time accepted. At zero time displacement
    is zero and average_velocity is the continuous extension initial_velocity.
    No inverse velocity sign inference from v², variable acceleration, trajectory
    collision, or multidimensional path-length claim.

    Exact Fraction arithmetic after input conversion/copy computes v=u+a*t,
    d=u*t+a*t²/2, mean=u+a*t/2 before independent float64 rounding. Avoids
    intermediate overflow and cancellation from rounded endpoint subtraction.
    Exact zeros and subnormals accepted; nonzero underflow or overflow rejects
    the entire call. No throughput claim.
    """
    arrays=[]
    for value in (initial_velocity,acceleration,elapsed_time):
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):arr=raw.astype(np.float64,copy=True)
        if not np.isfinite(arr).all():raise ValueError('Finite inputs required')
        arrays.append(arr)
    if any(a.shape!=arrays[0].shape for a in arrays[1:]):raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[2]<0):raise ValueError('Nonnegative elapsed time required')
    outputs=[[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        u,a,t=(Fraction(float(v)) for v in row)
        for bucket,value in zip(outputs,(u+a*t,u*t+a*t*t/2,u+a*t/2)):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Output outside float64 range') from error
            if not np.isfinite(rounded) or (value and rounded==0):raise ValueError('Nonzero output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
