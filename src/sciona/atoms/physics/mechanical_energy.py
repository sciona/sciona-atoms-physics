"""Constant-force motion and mechanical energy with exact intermediates."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_mechanical_energy(mass: AbstractArray, force: AbstractArray,
                              initial_position: AbstractArray, initial_velocity: AbstractArray,
                              elapsed_time: AbstractArray) -> tuple[AbstractArray, AbstractArray, AbstractArray,
                                                                    AbstractArray, AbstractArray, AbstractArray]:
    if any(a.shape != mass.shape for a in (force, initial_position, initial_velocity, elapsed_time)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=mass.shape, dtype='float64') for _ in range(6))


@register_atom(witness_mechanical_energy)
def mechanical_energy(mass: NDArray[np.float64], force: NDArray[np.float64],
                      initial_position: NDArray[np.float64], initial_velocity: NDArray[np.float64],
                      elapsed_time: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64],
                                                                NDArray[np.float64], NDArray[np.float64],
                                                                NDArray[np.float64], NDArray[np.float64]]:
    """Return final_position, final_velocity, kinetic_energy, potential_energy,
    total_energy, and work in SI units for one-dimensional Newtonian motion.

    Positive constant mass, constant signed net force, finite initial position
    and velocity, nonnegative duration. The conservative potential is U=-F*x,
    with zero chosen at x=0. No other work or dissipation is included. Zero
    force, zero duration and velocity reversal are supported. Work is F*(x-x0),
    not force times path length. No relativistic or variable-force claim.

    Inputs are nonempty real float64-compatible arrays of identical shape;
    scalars are accepted, broadcasting is not. Inputs are copied. Exact Fraction
    arithmetic after conversion evaluates all quantities before independent
    float64 rounding. K and U are computed from exact model coordinates, not
    rounded outputs; rounded K+U need not equal rounded total_energy. Total
    energy is conserved in the exact model. Exact zero and subnormals are
    accepted; nonzero underflow or overflow in any output rejects the call.
    """
    arrays = []
    for value in (mass, force, initial_position, initial_velocity, elapsed_time):
        raw = np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            array = raw.astype(np.float64, copy=True)
        if not np.isfinite(array).all():
            raise ValueError('Finite inputs required')
        arrays.append(array)
    if any(a.shape != arrays[0].shape for a in arrays[1:]):
        raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[0] <= 0) or np.any(arrays[4] < 0):
        raise ValueError('Positive mass and nonnegative elapsed time required')
    outputs = [[] for _ in range(6)]
    for row in zip(*(a.flat for a in arrays)):
        m, f, x0, u, t = (Fraction(float(v)) for v in row)
        v = u+f*t/m
        d = u*t+f*t*t/(2*m)
        x = x0+d
        kinetic = m*v*v/2
        potential = -f*x
        values = (x, v, kinetic, potential, kinetic+potential, f*d)
        for bucket, value in zip(outputs, values):
            try:
                rounded = float(value)
            except OverflowError as error:
                raise ValueError('Output outside float64 range') from error
            if not np.isfinite(rounded) or (value and rounded == 0):
                raise ValueError('Nonzero output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
