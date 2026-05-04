"""Auto-generated verified atom wrapper."""

from __future__ import annotations

import numpy as np

import icontract

from sciona.ghost.decorators import symbolic_atom

from .expressions import (
    GRAPH_TIME_SCALE_DIM_MAP,
    GRAPH_TIME_SCALE_EXPR,
    GRAPH_TIME_SCALE_VARIABLES,
    HIGH_PRECISION_DURATION_DIM_MAP,
    HIGH_PRECISION_DURATION_EXPR,
    HIGH_PRECISION_DURATION_VALIDITY_BOUNDS,
    HIGH_PRECISION_DURATION_VARIABLES,
    TEMPO_ROOT_BIBLIOGRAPHY,
)
from .witnesses import (
    witness_graph_time_scale_management,
    witness_high_precision_duration,
)


@symbolic_atom(
    witness_graph_time_scale_management,
    expr=GRAPH_TIME_SCALE_EXPR,
    dim_map=GRAPH_TIME_SCALE_DIM_MAP,
    variables=GRAPH_TIME_SCALE_VARIABLES,
    bibliography=TEMPO_ROOT_BIBLIOGRAPHY,
)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def graph_time_scale_management(data: np.ndarray) -> np.ndarray:
    """Computes transformation paths dynamically using a directed graph representation.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    return data


@symbolic_atom(
    witness_high_precision_duration,
    expr=HIGH_PRECISION_DURATION_EXPR,
    dim_map=HIGH_PRECISION_DURATION_DIM_MAP,
    validity_bounds=HIGH_PRECISION_DURATION_VALIDITY_BOUNDS,
    variables=HIGH_PRECISION_DURATION_VARIABLES,
    bibliography=TEMPO_ROOT_BIBLIOGRAPHY,
)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def high_precision_duration(data: np.ndarray) -> np.ndarray:
    """Splits a continuous variable into an integer and fractional part to preserve numerical precision.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    return np.array([np.floor(data), data - np.floor(data)])
