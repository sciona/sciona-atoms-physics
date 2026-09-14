"""Exactly accumulated moments for a finite normalized real distribution."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_weighted_population_variance(values: AbstractArray, weights: AbstractArray) -> tuple[AbstractArray, AbstractArray]:
    if len(values.shape) < 1 or values.shape != weights.shape:
        raise ValueError('Identical (...,N) shapes required')
    return tuple(AbstractArray(shape=values.shape[:-1], dtype='float64') for _ in range(2))


@register_atom(witness_weighted_population_variance)
def weighted_population_variance(values: NDArray[np.float64], weights: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return mean and population variance along the final axis.

    Values and weights must be finite real, identical nonempty (...,N) arrays,
    converted to float64. Require N>0, nonnegative weights and positive total
    weight in each batch. No broadcasting. Arbitrary positive weight scale is
    normalized internally; zero-weight values are permitted but must be finite.

    A normalized linear expectation gives E[(x-E[x])²]=E[x²]-E[x]². Exact
    rational arithmetic on the converted binary64 values accumulates the mean
    and centered second moment, avoiding cancellation and intermediate overflow.
    Each output rounds independently to float64; variance uses the exact mean.
    Exact zeros and subnormals are supported; nonzero underflow to zero or
    nonfinite outputs fail. Inputs remain unchanged.

    Mean has the units of values and variance their square. This is a finite
    weighted population distribution, not an unbiased sample estimator, standard
    deviation, signed measure or quadrature accuracy guarantee for a continuum.
    """
    arrays = []
    for value in (values, weights):
        raw = np.asarray(value)
        if raw.dtype.kind not in 'iuf' or raw.ndim < 1 or not raw.size:
            raise ValueError('Nonempty real (...,N) arrays required')
        with np.errstate(over='ignore', invalid='ignore'):
            converted = raw.astype(np.float64, copy=True)
        if not np.isfinite(converted).all():
            raise ValueError('Finite float64 inputs required')
        arrays.append(converted)
    values, weights = arrays
    if values.shape != weights.shape:
        raise ValueError('Identical shapes required without broadcasting')
    if np.any(weights < 0):
        raise ValueError('Nonnegative weights required')
    n = values.shape[-1]; outputs = [[], []]
    for row, weighted in zip(values.reshape(-1, n), weights.reshape(-1, n)):
        xs = [Fraction(float(x)) for x in row]
        ws = [Fraction(float(w)) for w in weighted]
        total = sum(ws)
        if total == 0:
            raise ValueError('Positive total weight required in every batch')
        mean = sum(w*x for w, x in zip(ws, xs))/total
        variance = sum(w*(x-mean)**2 for w, x in zip(ws, xs))/total
        for destination, exact in zip(outputs, [mean, variance]):
            try:
                rounded = float(exact)
            except OverflowError as error:
                raise ValueError('Moment exceeds finite float64 range') from error
            if not np.isfinite(rounded) or (exact and rounded == 0):
                raise ValueError('Moment exceeds representable nonzero float64 range')
            destination.append(rounded)
    return tuple(np.asarray(output, dtype=np.float64).reshape(values.shape[:-1]) for output in outputs)
