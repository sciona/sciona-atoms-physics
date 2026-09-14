"""Normalized scalar-wave interference and its fixed-amplitude ensemble mean."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_wave_interference(amplitude_a: AbstractArray, amplitude_b: AbstractArray,
                              relative_phase: AbstractArray) -> tuple[AbstractArray, AbstractArray,
                                                                      AbstractArray, AbstractArray,
                                                                      AbstractArray, AbstractArray]:
    if amplitude_a.shape != amplitude_b.shape or amplitude_b.shape != relative_phase.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=amplitude_a.shape, dtype='float64') for _ in range(6))


@register_atom(witness_wave_interference)
def wave_interference(amplitude_a: NDArray[np.float64], amplitude_b: NDArray[np.float64],
                      relative_phase: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64],
                                                                 NDArray[np.float64], NDArray[np.float64],
                                                                 NDArray[np.float64], NDArray[np.float64]]:
    """Return intensity, incoherent_mean, constructive, destructive, interference,
    and ratio for two normalized scalar waves of the same polarization/mode.

    Nonnegative finite amplitudes, not both zero; finite relative phase in
    radians. Common amplitude/intensity normalization, no absolute SI calibration.
    Intensity is the fixed-phase squared magnitude. Incoherent_mean assumes fixed
    amplitudes and zero averaged cosine, e.g. uniform relative phase. Constructive
    and destructive are phase extrema. Ratio is intensity/incoherent_mean; it is
    two only for equal nonzero amplitudes in phase, not all coherent waves.
    All-zero amplitudes are excluded because their ratio is undefined.

    Nonempty real float64-compatible equal shapes, scalars allowed, no
    broadcasting. Inputs are copied. Local 1200-digit arithmetic evaluates the
    positive expression (a-b)^2+4*a*b*cos(phase/2)^2 to avoid destructive-phase
    cancellation. Float64 phase values are used literally: rounded pi is not
    exact pi, and large phase values are not reduced using rounded float64 pi.
    All outputs are rounded independently; rounded sums or quotients need not
    match. Exact zero/subnormals accepted; nonzero output underflow/overflow
    rejects the call. No universal correct-rounding or throughput guarantee.
    """
    import mpmath
    arrays = []
    for value in (amplitude_a, amplitude_b, relative_phase):
        raw = np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            arr = raw.astype(np.float64, copy=True)
        if not np.isfinite(arr).all():
            raise ValueError('Finite inputs required')
        arrays.append(arr)
    if any(a.shape != arrays[0].shape for a in arrays[1:]):
        raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[0] < 0) or np.any(arrays[1] < 0) or np.any((arrays[0] == 0) & (arrays[1] == 0)):
        raise ValueError('Nonnegative amplitudes, not both zero, required')
    ctx = mpmath.mp.clone()
    ctx.dps = 1200
    outputs = [[] for _ in range(6)]
    for row in zip(*(a.flat for a in arrays)):
        a, b, phase = (ctx.mpf(float(v)) for v in row)
        mean = a*a+b*b
        maximum, minimum = (a+b)**2, (a-b)**2
        intensity = minimum+4*a*b*ctx.cos(phase/2)**2
        values = (intensity, mean, maximum, minimum, 2*a*b*ctx.cos(phase), intensity/mean)
        for bucket, value in zip(outputs, values):
            rounded = float(value)
            if not np.isfinite(rounded) or (value != 0 and rounded == 0):
                raise ValueError('Output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
