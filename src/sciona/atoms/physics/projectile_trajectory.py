"""Corrected ideal-projectile trajectory with exact converted-input algebra."""
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_projectile_trajectory(x: AbstractArray, x0: AbstractArray, y0: AbstractArray,
                                  vx0: AbstractArray, vy0: AbstractArray, gravity: AbstractArray) -> tuple[AbstractArray, AbstractArray]:
    if any(a.shape != x.shape for a in [x0, y0, vx0, vy0, gravity]):
        raise ValueError('Identical shapes required')
    return (AbstractArray(shape=x.shape, dtype='float64'), AbstractArray(shape=x.shape, dtype='float64'))


@register_atom(witness_projectile_trajectory)
def projectile_trajectory(x: NDArray[np.float64], x0: NDArray[np.float64], y0: NDArray[np.float64],
                          vx0: NDArray[np.float64], vy0: NDArray[np.float64], gravity: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return elapsed time and height at x for constant downward acceleration.

    All inputs are finite real arrays with identical nonempty shape (including
    scalar arrays), converted to float64. SI units: x/x0/y0 in m, vx0/vy0 in m/s,
    gravity in m/s². Require vx0!=0, gravity>=0 and (x-x0)/vx0>=0. Either horizontal
    direction is supported. Output time is s; height is m, positive upward.

    t=(x-x0)/vx0 and y=y0+vy0*t-gravity*t²/2, with exact rational arithmetic on
    converted binary64 values before independently rounding each output. Height
    uses exact t, not rounded output time. Nonzero results rounding to zero and
    nonfinite outputs fail; exact zeros and subnormals are supported.

    Ideal point-particle, no-drag, constant-acceleration kinematics only; no
    collision/terrain cutoff, varying gravity, wind or validity beyond that
    regime. Zero gravity is the inertial limit. Inputs are never mutated.
    """
    arrays = []
    for value in (x, x0, y0, vx0, vy0, gravity):
        raw = np.asarray(value)
        if raw.dtype.kind not in 'iuf' or not raw.size:
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            converted = raw.astype(np.float64, copy=True)
        if not np.isfinite(converted).all():
            raise ValueError('Finite float64 inputs required')
        arrays.append(converted)
    if any(a.shape != arrays[0].shape for a in arrays):
        raise ValueError('Identical shapes required without broadcasting')
    if np.any(arrays[3] == 0) or np.any(arrays[5] < 0):
        raise ValueError('Nonzero horizontal velocity and nonnegative gravity required')
    times, heights = [], []
    for values in zip(*(a.flat for a in arrays)):
        position, origin, initial_height, vx, vy, g = map(lambda v: Fraction(float(v)), values)
        elapsed = (position-origin)/vx
        if elapsed < 0:
            raise ValueError('Requested position precedes the initial time')
        height = initial_height+vy*elapsed-g*elapsed*elapsed/2
        outputs = []
        for value in (elapsed, height):
            try:
                rounded = float(value)
            except OverflowError as error:
                raise ValueError('Trajectory output exceeds finite float64 range') from error
            if not np.isfinite(rounded) or (value and rounded == 0):
                raise ValueError('Trajectory output exceeds representable nonzero float64 range')
            outputs.append(rounded)
        times.append(outputs[0]); heights.append(outputs[1])
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in [times, heights])
