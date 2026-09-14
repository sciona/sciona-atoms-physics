"""Undamped linear spring motion released from rest."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_spring_mass(mass: AbstractArray, stiffness: AbstractArray,
                        initial_displacement: AbstractArray, time: AbstractArray
                        ) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    if any(a.shape != mass.shape for a in (stiffness, initial_displacement, time)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=mass.shape, dtype='float64') for _ in range(4))


@register_atom(witness_spring_mass)
def spring_mass(mass: NDArray[np.float64], stiffness: NDArray[np.float64],
                initial_displacement: NDArray[np.float64], time: NDArray[np.float64]
                ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return natural angular frequency, displacement, velocity and acceleration.

    SI inputs: positive constant mass (kg), positive stiffness (N/m), signed
    initial displacement (m), and signed time since release (s). Zero initial
    velocity; linear spring is the net restoring force about equilibrium, with
    no damping or driving. Frequency is positive, in rad/s. This is the source
    cosine family, not arbitrary initial-velocity motion.

    Identical nonempty real float64-compatible arrays, including scalar arrays;
    no broadcasting. Every input is copied and converted to float64 first.
    Invocation-local mpmath at 1200 decimal digits evaluates sqrt(k/m), then
    A*cos(w*t), -A*w*sin(w*t), and -A*(k/m)*cos(w*t) before independent float64
    rounding. This avoids overflow of float64 ratios, products and phase: the
    largest phase from finite float64 inputs has fewer than 625 decimal digits.
    It also avoids computing acceleration from already-rounded displacement.
    Exact zeros and nonzero subnormals are allowed; nonzero underflow to zero or
    nonfinite output rejects the entire call. Large-phase accuracy treats input
    float64 values as exact; it does not infer precision in measured inputs.
    Synthetic reference checks are not a universal correct-rounding proof.
    Requires the precision extra; no throughput claim.
    """
    import mpmath
    arrays = []
    for i, value in enumerate((mass, stiffness, initial_displacement, time)):
        raw = np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            arr = raw.astype(np.float64, copy=True)
        if not np.isfinite(arr).all() or (i < 2 and np.any(arr <= 0)):
            raise ValueError('Finite inputs and positive mass/stiffness required')
        arrays.append(arr)
    if any(a.shape != arrays[0].shape for a in arrays[1:]):
        raise ValueError('Identical shapes required without broadcasting')
    ctx = mpmath.mp.clone()
    ctx.dps = 1200
    outputs = [[], [], [], []]
    for row in zip(*(a.flat for a in arrays)):
        m, k, A, t = (ctx.mpf(float(v)) for v in row)
        ratio = k/m
        omega = ctx.sqrt(ratio)
        phase = omega*t
        cosine, sine = ctx.cos(phase), ctx.sin(phase)
        values = (omega, A*cosine, -A*omega*sine, -A*ratio*cosine)
        for bucket, value in zip(outputs, values):
            rounded = float(value)
            if not np.isfinite(rounded) or (value != 0 and rounded == 0):
                raise ValueError('Output outside nonzero float64 representable range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
