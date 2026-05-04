"""Symbolic invariants for AstroFlow dedispersion atoms."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS


(
    output_sample,
    input_sum,
    nchans,
    dm_steps,
    time_downsample,
    down_ndata,
    delay_samples,
    shared_mem_size,
    block_dim_x,
) = sp.symbols(
    "output_sample input_sum nchans dm_steps time_downsample down_ndata "
    "delay_samples shared_mem_size block_dim_x"
)


DEDISPERSION_KERNEL_EXPR = sp.Eq(output_sample, input_sum / nchans)

DEDISPERSION_KERNEL_DIM_MAP = {
    "output_sample": DIMENSIONLESS,
    "input_sum": DIMENSIONLESS,
    "nchans": DIMENSIONLESS,
    "dm_steps": DIMENSIONLESS,
    "time_downsample": DIMENSIONLESS,
    "down_ndata": DIMENSIONLESS,
    "delay_samples": DIMENSIONLESS,
    "shared_mem_size": DIMENSIONLESS,
    "block_dim_x": DIMENSIONLESS,
}

DEDISPERSION_KERNEL_VARIABLES = {
    "input_sum": "input",
    "delay_samples": "input",
    "nchans": "parameter",
    "dm_steps": "parameter",
    "time_downsample": "parameter",
    "down_ndata": "parameter",
    "shared_mem_size": "parameter",
    "block_dim_x": "parameter",
    "output_sample": "output",
}

DEDISPERSION_KERNEL_VALIDITY_BOUNDS = {
    "nchans": (1.0, None),
    "dm_steps": (1.0, None),
    "time_downsample": (1.0, None),
    "down_ndata": (1.0, None),
    "shared_mem_size": (0.0, None),
    "block_dim_x": (1.0, None),
}

DEDISPERSION_KERNEL_BIBLIOGRAPHY = ["astroflow2025", "repo_astroflow"]
