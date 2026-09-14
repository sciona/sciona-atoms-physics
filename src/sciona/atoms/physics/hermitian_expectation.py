"""Finite-dimensional Hermitian expectation with exact converted-input algebra."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_hermitian_expectation(operator: AbstractArray, state: AbstractArray) -> AbstractArray:
    if len(state.shape) < 1 or len(operator.shape) != len(state.shape)+1:
        raise ValueError('Operator (...,N,N) and state (...,N) required')
    if operator.shape[:-2] != state.shape[:-1] or operator.shape[-2:] != (state.shape[-1], state.shape[-1]):
        raise ValueError('Exact batch and basis shape agreement required')
    return AbstractArray(shape=state.shape[:-1], dtype='float64')


@register_atom(witness_hermitian_expectation)
def hermitian_expectation(operator: NDArray[np.complex128], state: NDArray[np.complex128]) -> NDArray[np.float64]:
    """Compute real (state† operator state)/(state† state) without normalization loss.

    Inputs: finite numeric operator (...,N,N), state (...,N), N>0; identical
    nonempty batch shapes, no broadcasting. Inputs convert to complex128 before
    algebra. Operator must be exactly Hermitian after conversion; no tolerance
    or silent symmetrization. State must be nonzero in every batch member.

    Components use a common orthonormal basis. The expectation has the units
    of the operator. Arbitrary finite nonzero state scale is allowed; dividing
    by the positive norm gives the normalized expectation. This implements
    finite-dimensional pure-state algebra, not domain claims for unbounded
    infinite-dimensional operators or measurement sampling.

    Rational arithmetic on binary64 components forms the real quadratic form
    and norm exactly before a single float64 rounding. Exact zeros/subnormals
    are supported; nonzero underflow to zero and nonfinite output are rejected.
    No input mutation or performance claim.
    """
    arrays = []
    for value in (operator, state):
        raw = np.asarray(value)
        if raw.dtype.kind not in 'iufc' or not raw.size:
            raise ValueError('Nonempty numeric inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            converted = raw.astype(np.complex128, copy=True)
        if not np.isfinite(converted).all():
            raise ValueError('Finite complex128 inputs required')
        arrays.append(converted)
    matrix, vector = arrays
    if vector.ndim < 1 or matrix.ndim != vector.ndim+1 or matrix.shape[:-2] != vector.shape[:-1] or matrix.shape[-2:] != (vector.shape[-1], vector.shape[-1]):
        raise ValueError('Exact operator (...,N,N) and state (...,N) shape agreement required')
    if not np.array_equal(matrix, matrix.swapaxes(-1, -2).conj()):
        raise ValueError('Exactly Hermitian operator required')
    n = vector.shape[-1]
    results = []
    for a, psi in zip(matrix.reshape(-1, n, n), vector.reshape(-1, n)):
        parts = [(Fraction(float(z.real)), Fraction(float(z.imag))) for z in psi]
        norm = sum(x*x+y*y for x, y in parts)
        if not norm:
            raise ValueError('Nonzero state required in every batch member')
        quadratic = Fraction(0)
        for i, (x, y) in enumerate(parts):
            quadratic += Fraction(float(a[i, i].real))*(x*x+y*y)
            for j in range(i+1, n):
                u, v = parts[j]
                c, d = Fraction(float(a[i, j].real)), Fraction(float(a[i, j].imag))
                quadratic += 2*(x*(c*u-d*v)+y*(c*v+d*u))
        exact = quadratic/norm
        try:
            rounded = float(exact)
        except OverflowError as error:
            raise ValueError('Expectation exceeds finite float64 range') from error
        if not np.isfinite(rounded) or (exact and rounded == 0):
            raise ValueError('Expectation exceeds representable nonzero float64 range')
        results.append(rounded)
    return np.asarray(results, dtype=np.float64).reshape(vector.shape[:-1])
