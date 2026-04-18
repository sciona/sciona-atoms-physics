from __future__ import annotations

from sciona.ghost.abstract import AbstractArray, AbstractScalar, AbstractSignal


def _coerce_dim(value: object, default: int = 1) -> int:
    """Best-effort conversion of scalar metadata to a concrete dimension."""
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        shape = getattr(value, "shape", ())
        if shape:
            try:
                return max(1, int(shape[0]))
            except (TypeError, ValueError, IndexError):
                return default
        return default


def witness_dedispersionkernel(
    input_data: AbstractSignal,
    delay_table: AbstractArray,
    dm_steps: AbstractScalar,
    time_downsample: AbstractScalar,
    down_ndata: AbstractScalar,
    nchans: AbstractScalar,
    shared_mem_size: AbstractScalar,
    block_dim_x: AbstractScalar,
) -> AbstractSignal:
    """Shape-and-type check for dedispersion kernel output metadata."""
    del delay_table, nchans, shared_mem_size, block_dim_x
    result = AbstractSignal(
        shape=(_coerce_dim(dm_steps), _coerce_dim(down_ndata)),
        dtype="float64",
        sampling_rate=getattr(input_data, "sampling_rate", 44100.0) / max(_coerce_dim(time_downsample), 1),
        domain="time",
    )
    return result
