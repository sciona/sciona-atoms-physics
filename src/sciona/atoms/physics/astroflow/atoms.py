"""Auto-generated atom wrappers following the sciona pattern."""

from __future__ import annotations

import numpy as np

import icontract
from sciona.ghost.registry import register_atom
from .witnesses import witness_dedispersionkernel

# Witness functions should be imported from the generated witnesses module

@register_atom(witness_dedispersionkernel)
@icontract.require(lambda input_data: input_data is not None, "input_data cannot be None")
@icontract.require(lambda delay_table: delay_table is not None, "delay_table cannot be None")
@icontract.require(lambda dm_steps: dm_steps is not None, "dm_steps cannot be None")
@icontract.require(lambda time_downsample: time_downsample is not None, "time_downsample cannot be None")
@icontract.require(lambda down_ndata: down_ndata is not None, "down_ndata cannot be None")
@icontract.require(lambda nchans: nchans is not None, "nchans cannot be None")
@icontract.require(lambda shared_mem_size: shared_mem_size is not None, "shared_mem_size cannot be None")
@icontract.require(lambda block_dim_x: block_dim_x is not None, "block_dim_x cannot be None")
@icontract.ensure(lambda result: result is not None, "DedispersionKernel output must not be None")
def dedispersionkernel(input_data: "np.ndarray[np.generic]", delay_table: "np.ndarray[np.generic]", dm_steps: int, time_downsample: int, down_ndata: int, nchans: int, shared_mem_size: int, block_dim_x: int) -> "np.ndarray[np.generic]":
    """Applies a dedispersion kernel to input data using a pre-computed delay table, transforming the data across different dispersion measure (DM) steps.

    Args:
        input_data: Raw observational data array.
        delay_table: Table of delays to apply for each channel and DM step.
        dm_steps: Number of dispersion measures to process.
        time_downsample: Factor by which to downsample the time series.
        down_ndata: The size of the output data array after downsampling.
        nchans: Number of frequency channels in the input data.
        shared_mem_size: Size of shared memory for the computational kernel (e.g., on a GPU).
        block_dim_x: The block dimension in the x-axis for the computational kernel.

    Returns:
        The transformed, dedispersed data.
    """
    # CPU reimplementation of GPU dedispersion kernel
    input_arr = np.asarray(input_data)
    delays = np.asarray(delay_table, dtype=np.intp)

    # Output: (dm_steps, down_ndata)
    output = np.zeros((dm_steps, down_ndata), dtype=input_arr.dtype)

    for dm_idx in range(dm_steps):
        for t_out in range(down_ndata):
            t_start = t_out * time_downsample
            acc = 0.0
            for chan in range(nchans):
                delay = int(delays[dm_idx * nchans + chan]) if delays.ndim == 1 else int(delays[dm_idx, chan])
                t_in = t_start + delay
                if 0 <= t_in < input_arr.shape[-1] if input_arr.ndim == 1 else input_arr.shape[0]:
                    if input_arr.ndim == 1:
                        acc += float(input_arr[t_in])
                    else:
                        acc += float(input_arr[t_in, chan] if input_arr.ndim == 2 else input_arr[chan, t_in])
            output[dm_idx, t_out] = acc / max(nchans, 1)
    return output