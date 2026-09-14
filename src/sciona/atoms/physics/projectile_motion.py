"""Full time-based ideal projectile state with high-precision intermediates."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_projectile_motion(initial_x: AbstractArray, initial_y: AbstractArray,
                              initial_speed: AbstractArray, launch_angle: AbstractArray,
                              gravity: AbstractArray, elapsed_time: AbstractArray
                              ) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    if any(a.shape != initial_x.shape for a in (initial_y, initial_speed, launch_angle, gravity, elapsed_time)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=initial_x.shape, dtype='float64') for _ in range(4))


@register_atom(witness_projectile_motion)
def projectile_motion(initial_x: NDArray[np.float64], initial_y: NDArray[np.float64],
                      initial_speed: NDArray[np.float64], launch_angle: NDArray[np.float64],
                      gravity: NDArray[np.float64], elapsed_time: NDArray[np.float64]
                      ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return x, y, vx, vy for ideal motion under constant downward gravity.

    SI positions, speed, gravity and time; angle in radians from positive x.
    Upward-positive y; initial_speed, gravity, elapsed_time are nonnegative.
    Initial positions and angle may be any finite real values. No drag, terrain
    or collision cutoff; zero gravity is the inertial limit. Zero speed and
    time are allowed; no division by horizontal velocity or speed.

    Equal nonempty real float64-compatible shapes; scalar arrays allowed, no
    broadcasting. Inputs copied. Local 2000-digit calculations combine terms
    before independently rounding each output. Literal converted phase is used:
    float64 pi/2 is not exact vertical and is not snapped. Very large finite
    angles supported without reducing by rounded float64 pi. Exact zeros and
    subnormals accepted; nonzero output underflow or overflow rejects the call.
    No universal correct-rounding, throughput or rounded-energy guarantee.
    """
    import mpmath
    arrays = []
    for value in (initial_x, initial_y, initial_speed, launch_angle, gravity, elapsed_time):
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
    if any(np.any(arrays[i] < 0) for i in [2, 4, 5]):
        raise ValueError('Nonnegative speed, gravity and elapsed time required')
    ctx = mpmath.mp.clone()
    ctx.dps = 2000
    outputs = [[] for _ in range(4)]
    for row in zip(*(a.flat for a in arrays)):
        x0, y0, speed, theta, g, t = (ctx.mpf(float(v)) for v in row)
        ux, uy = speed*ctx.cos(theta), speed*ctx.sin(theta)
        for bucket, value in zip(outputs, (x0+ux*t, y0+uy*t-g*t*t/2, ux, uy-g*t)):
            rounded = float(value)
            if not np.isfinite(rounded) or (value != 0 and rounded == 0):
                raise ValueError('Output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
