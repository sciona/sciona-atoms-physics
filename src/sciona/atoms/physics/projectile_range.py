"""Level-ground projectile flight, range and fixed-speed range maximum."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_projectile_range(launch_speed: AbstractArray, gravity: AbstractArray,
                             launch_angle: AbstractArray) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    if launch_speed.shape != gravity.shape or gravity.shape != launch_angle.shape:
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=launch_speed.shape, dtype='float64') for _ in range(4))


@register_atom(witness_projectile_range)
def projectile_range(launch_speed: NDArray[np.float64], gravity: NDArray[np.float64],
                     launch_angle: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return flight_time, horizontal_range, maximizing_angle, maximum_range.

    SI speed and gravity must be positive finite; angle is radians in
    [0, float64(pi/2)]. Equal nonempty real float64-compatible shapes, scalar
    arrays allowed, no broadcasting. No drag, constant gravity, level ground;
    maximum holds at fixed speed. Zero angle returns zero time/range as the
    limiting root merging with launch. float64(pi/2) is evaluated as its actual
    real value, slightly below mathematical pi/2, so its range is small positive.
    Returned maximizing_angle is rounded pi/4, while maximum_range evaluates
    the exact mathematical optimum independently of that rounded angle.

    Local 450-digit arithmetic avoids float64 intermediate overflow/underflow.
    Inputs copied to float64; finite subnormals accepted. Nonzero output rounding
    to zero or overflow rejects the call. Finite reference tests are not a
    universal correct-rounding proof. No unequal-height or drag optimization.
    """
    import mpmath
    arrays = []
    for value in (launch_speed, gravity, launch_angle):
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
    if np.any(arrays[0] <= 0) or np.any(arrays[1] <= 0):
        raise ValueError('Positive speed and gravity required')
    if np.any(arrays[2] < 0) or np.any(arrays[2] > np.pi/2):
        raise ValueError('Angle outside first quadrant')
    ctx = mpmath.mp.clone()
    ctx.dps = 450
    outputs = [[], [], [], []]
    for row in zip(*(a.flat for a in arrays)):
        v, g, theta = (ctx.mpf(float(x)) for x in row)
        flight = 2*v*ctx.sin(theta)/g
        distance = v*v*ctx.sin(2*theta)/g
        for bucket, value in zip(outputs, (flight, distance, ctx.pi/4, v*v/g)):
            rounded = float(value)
            if not np.isfinite(rounded) or (value != 0 and rounded == 0):
                raise ValueError('Output outside float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)
