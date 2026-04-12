"""Grouped Tempo.jl offset atoms mirroring the upstream `Tempo.offset` module."""

from __future__ import annotations

import math

import icontract
import numpy as np
from ageoa.ghost.registry import register_atom

from .witnesses import witness_offset_tt2tdb, witness_offset_tt2tdbh, witness_tt2tdb_offset


@register_atom(witness_offset_tt2tdb)
@icontract.require(lambda seconds: seconds is not None, "seconds cannot be None")
@icontract.ensure(lambda result: result is not None, "result must not be None")
def offset_tt2tdb(seconds: float) -> float:
    """Compute the Tempo.jl low-order TT->TDB offset approximation.

    Args:
        seconds: Time in seconds since the J2000 reference epoch.

    Returns:
        Offset in seconds for converting TT to TDB.
    """

    k = 1.657e-3
    eb = 1.671e-2
    m0 = 6.239996
    m1 = 1.99096871e-7
    g = m0 + m1 * seconds
    return k * math.sin(g + eb * math.sin(g))


@register_atom(witness_offset_tt2tdbh)
@icontract.require(lambda seconds: seconds is not None, "seconds cannot be None")
@icontract.ensure(lambda result: result is not None, "result must not be None")
def offset_tt2tdbh(seconds: float) -> float:
    """Compute the higher-accuracy Tempo.jl TT->TDB offset approximation.

    Args:
        seconds: Time in seconds since the J2000 reference epoch.

    Returns:
        Higher-accuracy TT to TDB offset in seconds.
    """

    century_to_seconds = 86400.0 * 36525.0
    t = seconds / century_to_seconds
    return (
        0.001657 * math.sin(628.3076 * t + 6.2401)
        + 0.000022 * math.sin(575.3385 * t + 4.2970)
        + 0.000014 * math.sin(1256.6152 * t + 6.1969)
        + 0.000005 * math.sin(606.9777 * t + 4.0212)
        + 0.000005 * math.sin(52.9691 * t + 0.4444)
        + 0.000002 * math.sin(21.3299 * t + 5.5431)
        + 0.000010 * t * math.sin(628.3076 * t + 4.2490)
    )


@register_atom(witness_tt2tdb_offset)
@icontract.require(lambda seconds: isinstance(seconds, (float, int, np.ndarray, np.number)), "seconds must be numeric")
@icontract.ensure(lambda result: result is not None, "result must not be None")
def tt2tdb_offset(seconds: float | np.ndarray) -> float | np.ndarray:
    """Compute the vectorized TT->TDB offset used by the older d12 ingest.

    Args:
        seconds: Scalar or array of elapsed seconds from the J2000 reference epoch.

    Returns:
        Scalar or array of TT to TDB offsets in seconds, shape-preserving for arrays.
    """

    k = 1.657e-3
    eb = 1.671e-2
    m0 = 6.239996
    m1 = 1.99096871e-7
    g = m0 + m1 * np.asarray(seconds, dtype=float)
    result = k * np.sin(g + eb * np.sin(g))
    if np.isscalar(seconds):
        return float(result)
    return np.asarray(result, dtype=float)
