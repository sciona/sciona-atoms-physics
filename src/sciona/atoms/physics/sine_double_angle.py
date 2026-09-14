"""Real double-angle sine evaluated through the reviewed product identity."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_sine_double_angle(angle: AbstractArray) -> AbstractArray:
    return AbstractArray(shape=angle.shape,dtype='float64')


@register_atom(witness_sine_double_angle)
def sine_double_angle(angle: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return sin(2*x) through 2*sin(x)*cos(x), for real radians.

    Inputs are nonempty finite real arrays, including scalar arrays, converted
    to float64. Shape and inputs are preserved. No degree conversion, angle
    clipping or modular reduction in binary64 is performed. The doubled angle
    is never formed in float64, so every finite binary64 angle is admitted.

    An invocation-local mpmath context with 450 decimal digits evaluates the
    product before float64 conversion. This accommodates large arguments and
    small results without binary64 intermediate overflow. Accuracy is supported
    by the retained validation corpus, not a universal correctly-rounded proof.
    No complex-input, phase-unwrapping, interval or throughput claim.
    Requires the provider's precision optional dependency.
    """
    import mpmath
    raw=np.asarray(angle)
    if not raw.size or raw.dtype.kind not in 'iuf':
        raise ValueError('Nonempty real angles required')
    with np.errstate(over='ignore',invalid='ignore'):
        values=raw.astype(np.float64,copy=True)
    if not np.isfinite(values).all():
        raise ValueError('Finite float64 angles required')
    ctx=mpmath.mp.clone();ctx.dps=450
    outputs=[]
    for value in values.flat:
        x=ctx.mpf(float(value))
        y=2*ctx.sin(x)*ctx.cos(x)
        rounded=float(y)
        if not np.isfinite(rounded) or (y and rounded==0):
            raise ValueError('Result cannot be represented as nonzero float64')
        outputs.append(rounded)
    return np.asarray(outputs,dtype=np.float64).reshape(values.shape)
