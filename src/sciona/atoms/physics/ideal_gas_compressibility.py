"""Isothermal volume compressibility of an ideal gas."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_ideal_gas_compressibility(pressure: AbstractArray) -> AbstractArray:
    return AbstractArray(shape=pressure.shape, dtype='float64')


@register_atom(witness_ideal_gas_compressibility)
def ideal_gas_compressibility(pressure: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return kappa_T=-(1/V)*(partial V/partial P)_T=1/P in Pa^-1.

    Nonempty finite positive absolute pressures in pascals, including scalar
    arrays, are converted to float64. Shape and inputs are preserved. Caller
    establishes ideal-gas behavior with fixed positive temperature and amount in
    moles, PV=nRT with molar R. This is local isothermal compressibility, not isentropic compressibility or bulk modulus;
    no real-gas, phase-transition, finite-change or low-temperature applicability
    claim. The ideal-gas model must be valid at the supplied state.

    The exact reciprocal of the converted binary64 input is rounded once.
    Subnormal results are accepted; unrepresentable finite outputs are rejected.
    """
    raw = np.asarray(pressure)
    if not raw.size or raw.dtype.kind not in 'iuf':
        raise ValueError('Nonempty real pressures required')
    with np.errstate(over='ignore', invalid='ignore'):
        values = raw.astype(np.float64, copy=True)
    if not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError('Finite positive absolute pressures required')
    outputs = []
    for value in values.flat:
        try:
            result = float(1/Fraction(float(value)))
        except OverflowError as error:
            raise ValueError('Compressibility exceeds finite float64 range') from error
        if not np.isfinite(result) or result <= 0:
            raise ValueError('Compressibility outside positive finite float64 range')
        outputs.append(result)
    return np.asarray(outputs, dtype=np.float64).reshape(values.shape)
