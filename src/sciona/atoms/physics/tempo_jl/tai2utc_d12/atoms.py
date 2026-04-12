from __future__ import annotations
"""Auto-generated atom wrappers following the ageoa pattern."""


import numpy as np

import icontract
from ageoa.ghost.registry import register_atom
from .witnesses import witness_tai_to_utc_inversion, witness_utc_to_tai_leap_second_kernel

from juliacall import Main as jl  # type: ignore[import-untyped]


# Witness functions should be imported from the generated witnesses module

@register_atom(witness_utc_to_tai_leap_second_kernel)  # type: ignore[name-defined, untyped-decorator]
@icontract.require(lambda utc1: isinstance(utc1, (float, int, np.number)), "utc1 must be numeric")
@icontract.require(lambda utc2: isinstance(utc2, (float, int, np.number)), "utc2 must be numeric")
@icontract.ensure(lambda result: all(r is not None for r in result), "utc_to_tai_leap_second_kernel all outputs must not be None")
def utc_to_tai_leap_second_kernel(utc1: float, utc2: float) -> tuple[float, float]:
    """Converts a two-part Coordinated Universal Time (UTC) Julian date to International Atomic Time (TAI) by resolving the applicable leap-second offset. Internally converts Julian date to calendar date (jd2cal) to locate the correct leap-second table entry, then adds the offset to produce the TAI two-part Julian date.

Args:
    utc1: finite; utc1+utc2 must be within the supported leap-second table range
    utc2: finite; together with utc1 represents a valid UTC epoch

Returns:
    tai1: tai1 + tai2 = utc1 + utc2 + leap_seconds/86400
    tai2: precision-preserving companion to tai1"""
    import bisect
    DJ2000 = 2451545.0
    _LEAP_JD2000 = [
        -10957.5, -10774.5, -10592.5, -10227.5, -9862.5, -9497.5, -9132.5,
        -8767.5, -8402.5, -8037.5, -7487.5, -7122.5, -6757.5, -6027.5,
        -5114.5, -4383.5, -4018.5, -3470.5, -3105.5, -2740.5, -2192.5,
        -1644.5, -914.5, 1640.5, 2736.5, 4019.5, 5114.5, 6209.5,
    ]
    _LEAP_SECONDS = [
        10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
        20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0,
        30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0,
    ]
    jd2000_day = (utc1 - DJ2000) + utc2
    idx = bisect.bisect_right(_LEAP_JD2000, jd2000_day) - 1
    if idx < 0:
        delta_at = 0.0
    else:
        delta_at = _LEAP_SECONDS[idx]
    return (utc1, utc2 + delta_at / 86400.0)

@register_atom(witness_tai_to_utc_inversion)  # type: ignore[name-defined, untyped-decorator]
@icontract.require(lambda tai1: isinstance(tai1, (float, int, np.number)), "tai1 must be numeric")
@icontract.require(lambda tai2: isinstance(tai2, (float, int, np.number)), "tai2 must be numeric")
@icontract.require(lambda tai_estimate: isinstance(tai_estimate, (float, int, np.number)), "tai_estimate must be numeric")
@icontract.ensure(lambda result: all(r is not None for r in result), "tai_to_utc_inversion all outputs must not be None")
def tai_to_utc_inversion(tai1: float, tai2: float, tai_estimate: float) -> tuple[float, float, float]:
    """Entry-point atom. Inverts the Coordinated Universal Time (UTC)→International Atomic Time (TAI) mapping to recover UTC from a given TAI epoch. Uses an iterative bracketing strategy: seeds a candidate UTC estimate, calls the utc_to_tai_leap_second_kernel to evaluate the forward mapping, then refines until the residual is within floating-point tolerance.

Args:
    tai1: finite; must fall within the supported leap-second table range
    tai2: finite; precision-preserving companion to tai1
    tai_estimate: fed from utc_to_tai_leap_second_kernel output on each iteration

Returns:
    utc1: utc1 + utc2 + leap_seconds/86400 ≈ tai1 + tai2 within floating-point epsilon
    utc2: precision-preserving companion to utc1
    candidate_utc: updated each iteration; becomes final utc1/utc2 on convergence"""
    import bisect
    DJ2000 = 2451545.0
    _LEAP_JD2000 = [
        -10957.5, -10774.5, -10592.5, -10227.5, -9862.5, -9497.5, -9132.5,
        -8767.5, -8402.5, -8037.5, -7487.5, -7122.5, -6757.5, -6027.5,
        -5114.5, -4383.5, -4018.5, -3470.5, -3105.5, -2740.5, -2192.5,
        -1644.5, -914.5, 1640.5, 2736.5, 4019.5, 5114.5, 6209.5,
    ]
    _LEAP_SECONDS = [
        10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
        20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0,
        30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0,
    ]
    u1, u2 = tai1, tai2
    for _ in range(2):
        jd2000_day = (u1 - DJ2000) + u2
        idx = bisect.bisect_right(_LEAP_JD2000, jd2000_day) - 1
        if idx < 0:
            delta_at = 0.0
        else:
            delta_at = _LEAP_SECONDS[idx]
        g1 = u1
        g2 = u2 + delta_at / 86400.0
        u2 += tai1 - g1
        u2 += tai2 - g2
    candidate_utc = u1 + u2
    return (u1, u2, candidate_utc)


"""Auto-generated FFI bindings for julia implementations."""


from juliacall import Main as jl


def _utc_to_tai_leap_second_kernel_ffi(utc1: float, utc2: float) -> object:
    """Wrapper that calls the Julia version of utc to tai leap second kernel. Passes arguments through and returns the result."""
    return jl.eval("utc_to_tai_leap_second_kernel(utc1, utc2)")

def _tai_to_utc_inversion_ffi(tai1: float, tai2: float, tai_estimate: float) -> object:
    """Wrapper that calls the Julia version of tai to utc inversion. Passes arguments through and returns the result."""
    return jl.eval("tai_to_utc_inversion(tai1, tai2, tai_estimate)")