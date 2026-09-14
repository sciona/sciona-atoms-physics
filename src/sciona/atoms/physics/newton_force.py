"""Conditional Newtonian gravitational interaction."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_newton_force(gravitational_constant: AbstractArray, mass_1: AbstractArray,
                          mass_2: AbstractArray, separation: AbstractArray
                          ) -> tuple[AbstractArray,AbstractArray,AbstractArray,AbstractArray]:
    if any(a.shape!=separation.shape for a in (gravitational_constant,mass_1,mass_2)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=separation.shape,dtype='float64') for _ in range(4))


@register_atom(witness_newton_force)
def newton_force(gravitational_constant: NDArray[np.float64], mass_1: NDArray[np.float64],
                  mass_2: NDArray[np.float64], separation: NDArray[np.float64]
                  ) -> tuple[NDArray[np.float64],NDArray[np.float64],NDArray[np.float64],NDArray[np.float64]]:
    """Return attractive force magnitude, acceleration magnitudes on bodies1/2, potential energy.

    Positive finite SI G (m^3 kg^-1 s^-2), two masses (kg), center separation (m).
    Newtonian point masses or exterior non-overlapping spherical bodies; caller
    establishes geometry/applicability. The assumed constitutive force law is
    G*m1*m2/r^2, not a consequence of Newton second law alone. Source independent
    mass scaling, inverse-square scaling and universal G require added premises;
    this numerical implementation does not certify the incomplete derivation.

    Outputs: G*m1*m2/r^2 in N, G*m2/r^2 and G*m1/r^2 in m/s^2, and
    -G*m1*m2/r in J with potential zero at infinity. Acceleration1 belongs to
    mass1. Magnitudes only, no direction vector, orbit integration, arbitrary
    extended-body or relativistic model. Both masses may be finite; the source
    circular test-mass argument is not used as a general two-body orbit proof.

    Identical nonempty real float64-compatible shapes, scalar support, no
    broadcasting. Inputs copied/converted first. Exact rational arithmetic over
    converted values, independently rounded once for each output; no intermediate
    overflow or division of a rounded force. Nonzero underflow or overflow rejects
    the call; subnormals allowed. No throughput claim.
    """
    arrays=[]
    for value in (gravitational_constant,mass_1,mass_2,separation):
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('Positive finite inputs required')
        arrays.append(a)
    if any(a.shape!=arrays[0].shape for a in arrays[1:]):raise ValueError('Identical shapes required without broadcasting')
    outputs=[[],[],[],[]]
    for row in zip(*(a.flat for a in arrays)):
        G,m1,m2,r=(Fraction(float(v)) for v in row)
        values=(G*m1*m2/(r*r),G*m2/(r*r),G*m1/(r*r),-G*m1*m2/r)
        for bucket,value in zip(outputs,values):
            try:rounded=float(value)
            except OverflowError as error:raise ValueError('Output overflow') from error
            if not np.isfinite(rounded) or rounded==0:raise ValueError('Output outside nonzero float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
