"""Volumetric expansion of an ideal gas at fixed pressure and amount."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_ideal_gas_expansion(temperature: AbstractArray) -> AbstractArray:
    return AbstractArray(shape=temperature.shape, dtype='float64')


@register_atom(witness_ideal_gas_expansion)
def ideal_gas_expansion(temperature: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return alpha=(1/V)*(partial V/partial T)_P=1/T in K^-1.

    Nonempty finite positive absolute temperatures in kelvin, including scalar
    arrays, are converted to float64. Shape and inputs are preserved. Caller
    establishes ideal-gas behavior with fixed positive pressure and amount in
    moles, PV=nRT with molar R. This is volumetric, not linear, expansion;
    no real-gas, phase-transition, finite-change or low-temperature applicability
    claim. The ideal-gas model must be valid at the supplied state.

    The exact reciprocal of the converted binary64 input is rounded once.
    Subnormal results are accepted; unrepresentable finite outputs are rejected.
    """
    raw = np.asarray(temperature)
    if not raw.size or raw.dtype.kind not in 'iuf':
        raise ValueError('Nonempty real temperatures required')
    with np.errstate(over='ignore', invalid='ignore'):
        values = raw.astype(np.float64, copy=True)
    if not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError('Finite positive absolute temperatures required')
    outputs = []
    for value in values.flat:
        try:
            result = float(1/Fraction(float(value)))
        except OverflowError as error:
            raise ValueError('Expansion exceeds finite float64 range') from error
        if not np.isfinite(result) or result <= 0:
            raise ValueError('Expansion outside positive finite float64 range')
        outputs.append(result)
    return np.asarray(outputs, dtype=np.float64).reshape(values.shape)
