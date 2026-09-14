"""Endpoint kinetic energies and signed net translational work."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_work_energy(mass: AbstractArray, initial_velocity: AbstractArray, final_velocity: AbstractArray
                        ) -> tuple[AbstractArray,AbstractArray,AbstractArray]:
    if mass.shape!=initial_velocity.shape or mass.shape!=final_velocity.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=mass.shape,dtype='float64') for _ in range(3))


@register_atom(witness_work_energy)
def work_energy(mass: NDArray[np.float64], initial_velocity: NDArray[np.float64], final_velocity: NDArray[np.float64]
                ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return initial KE, final KE and signed net work, in joules.

    Inputs are positive constant mass in kg and signed one-dimensional endpoint
    velocities in m/s, finite real float64-compatible arrays of identical
    nonempty shape including scalars. No broadcasting. Outputs are m*v1^2/2,
    m*v2^2/2 and m*(v2^2-v1^2)/2. Work is accumulated from the initial endpoint.
    Caller establishes consistent classical constant-mass endpoints; the source
    derivation assumes constant net force. Zero force entails unchanged velocity.
    This evaluates endpoint energies; it does not reconstruct a trajectory or
    certify force/endpoint consistency. No individual-force-only work, heat,
    rotational, variable-mass or relativistic energy claim.

    Exact rational arithmetic on converted float64 inputs precedes independent
    output rounding. Work is not computed by subtracting rounded energies.
    All outputs must be finite representable; exact zeros and subnormals are
    accepted, nonzero underflow to zero and overflow rejected. Inputs and shape
    preserved. No throughput claim.
    """
    arrays=[]
    for value in [mass,initial_velocity,final_velocity]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all():raise ValueError('Finite inputs required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays):raise ValueError('Identical shapes required')
    if np.any(arrays[0]<=0):raise ValueError('Positive mass required')
    outputs=[[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        m,u,v=map(lambda x:Fraction(float(x)),row)
        first,last=m*u*u/2,m*v*v/2
        for bucket,value in zip(outputs,[first,last,last-first]):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Energy outside float64 range') from error
            if not np.isfinite(rounded) or (value and rounded==0):raise ValueError('Nonzero energy outside representable float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
