"""Auto-generated atom wrappers following the sciona pattern."""

from __future__ import annotations

import icontract
from sciona.ghost.decorators import symbolic_atom

from .expressions import (
    CAL2JD_DIM_MAP,
    CAL2JD_EXPR,
    CAL2JD_VARIABLES,
    CALENDAR_VALIDITY_BOUNDS,
    CALHMS2JD_DIM_MAP,
    CALHMS2JD_EXPR,
    CALHMS2JD_VARIABLES,
    FD2HMS_DIM_MAP,
    FD2HMS_EXPR,
    FD2HMS_VARIABLES,
    FD2HMSF_DIM_MAP,
    FD2HMSF_EXPR,
    FD2HMSF_VARIABLES,
    FIND_DAY_DIM_MAP,
    FIND_DAY_EXPR,
    FIND_DAY_VARIABLES,
    FIND_DAYINYEAR_DIM_MAP,
    FIND_DAYINYEAR_EXPR,
    FIND_DAYINYEAR_VARIABLES,
    FIND_MONTH_DIM_MAP,
    FIND_MONTH_EXPR,
    FIND_MONTH_VARIABLES,
    FIND_YEAR_DIM_MAP,
    FIND_YEAR_EXPR,
    FIND_YEAR_VARIABLES,
    HMS2FD_DIM_MAP,
    HMS2FD_EXPR,
    HMS2FD_VARIABLES,
    ISLEAPYEAR_DIM_MAP,
    ISLEAPYEAR_EXPR,
    ISLEAPYEAR_VARIABLES,
    JD2CAL_DIM_MAP,
    JD2CAL_EXPR,
    JD2CAL_VARIABLES,
    JD2CALHMS_DIM_MAP,
    JD2CALHMS_EXPR,
    JD2CALHMS_VARIABLES,
    JD_CONSTANTS,
    LASTJ2000DAYOFYEAR_DIM_MAP,
    LASTJ2000DAYOFYEAR_EXPR,
    LASTJ2000DAYOFYEAR_VARIABLES,
    LEAP_SECOND_VALIDITY_BOUNDS,
    TAI2UTC_DIM_MAP,
    TAI2UTC_EXPR,
    TAI2UTC_VARIABLES,
    TEMPO_CALENDAR_BIBLIOGRAPHY,
    TIME_CONSTANTS,
    TIME_OF_DAY_VALIDITY_BOUNDS,
    UTC2TAI_DIM_MAP,
    UTC2TAI_EXPR,
    UTC2TAI_VARIABLES,
)
from .witnesses import witness_cal2jd, witness_calhms2jd, witness_fd2hms, witness_fd2hmsf, witness_find_day, witness_find_dayinyear, witness_find_month, witness_find_year, witness_hms2fd, witness_isleapyear, witness_jd2cal, witness_jd2calhms, witness_lastj2000dayofyear, witness_tai2utc, witness_utc2tai

from juliacall import Main as jl


# Witness functions should be imported from the generated witnesses module

@symbolic_atom(
    witness_isleapyear,
    expr=ISLEAPYEAR_EXPR,
    dim_map=ISLEAPYEAR_DIM_MAP,
    variables=ISLEAPYEAR_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
    skip_dim_check=True,
)
@icontract.require(lambda year: year is not None, "year cannot be None")
@icontract.ensure(lambda result: result is not None, "Isleapyear output must not be None")
def isleapyear(year: int) -> bool:
    """Isleapyear.

    Args:
        year (int): Description.

    Returns:
        bool: Description.
    """
    return year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)

@symbolic_atom(
    witness_find_dayinyear,
    expr=FIND_DAYINYEAR_EXPR,
    dim_map=FIND_DAYINYEAR_DIM_MAP,
    validity_bounds={
        "month": CALENDAR_VALIDITY_BOUNDS["month"],
        "day": CALENDAR_VALIDITY_BOUNDS["day"],
        "dayinyear": CALENDAR_VALIDITY_BOUNDS["dayinyear"],
    },
    variables=FIND_DAYINYEAR_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda month: month is not None, "month cannot be None")
@icontract.require(lambda day: day is not None, "day cannot be None")
@icontract.require(lambda isleap: isleap is not None, "isleap cannot be None")
@icontract.ensure(lambda result: result is not None, "Find Dayinyear output must not be None")
def find_dayinyear(month: int, day: int, isleap: bool) -> int:
    """Find dayinyear.

    Args:
        month (int): Description.
        day (int): Description.
        isleap (bool): Description.

    Returns:
        int: Description.
    """
    _PREV_MONTH_END_LEAP = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    _PREV_MONTH_END = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    if isleap:
        return day + _PREV_MONTH_END_LEAP[month - 1]
    return day + _PREV_MONTH_END[month - 1]

@symbolic_atom(
    witness_find_year,
    expr=FIND_YEAR_EXPR,
    dim_map=FIND_YEAR_DIM_MAP,
    validity_bounds={"dayinyear": CALENDAR_VALIDITY_BOUNDS["dayinyear"]},
    variables=FIND_YEAR_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda d: d is not None, "d cannot be None")
@icontract.ensure(lambda result: result is not None, "Find Year output must not be None")
def find_year(d: float) -> int:
    """Find year.

    Args:
        d (float): Description.

    Returns:
        int: Description.
    """
    j2d = int(d)
    year = (400 * j2d + 292194288) // 146097
    if j2d <= lastj2000dayofyear(year - 1):
        year -= 1
    return year

@symbolic_atom(
    witness_find_month,
    expr=FIND_MONTH_EXPR,
    dim_map=FIND_MONTH_DIM_MAP,
    validity_bounds={
        "dayinyear": CALENDAR_VALIDITY_BOUNDS["dayinyear"],
        "month": CALENDAR_VALIDITY_BOUNDS["month"],
        "day": CALENDAR_VALIDITY_BOUNDS["day"],
    },
    variables=FIND_MONTH_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda dayinyear: dayinyear is not None, "dayinyear cannot be None")
@icontract.require(lambda isleap: isleap is not None, "isleap cannot be None")
@icontract.ensure(lambda result: result is not None, "Find Month output must not be None")
def find_month(dayinyear: int, isleap: bool) -> int:
    """Find month.

    Args:
        dayinyear (int): Description.
        isleap (bool): Description.

    Returns:
        int: Description.
    """
    offset = 313 if isleap else 323
    if dayinyear < 32:
        return 1
    return (10 * dayinyear + offset) // 306

@symbolic_atom(
    witness_find_day,
    expr=FIND_DAY_EXPR,
    dim_map=FIND_DAY_DIM_MAP,
    validity_bounds={
        "dayinyear": CALENDAR_VALIDITY_BOUNDS["dayinyear"],
        "month": CALENDAR_VALIDITY_BOUNDS["month"],
        "day": CALENDAR_VALIDITY_BOUNDS["day"],
    },
    variables=FIND_DAY_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda dayinyear: dayinyear is not None, "dayinyear cannot be None")
@icontract.require(lambda month: month is not None, "month cannot be None")
@icontract.require(lambda isleap: isleap is not None, "isleap cannot be None")
@icontract.ensure(lambda result: result is not None, "Find Day output must not be None")
def find_day(dayinyear: int, month: int, isleap: bool) -> int:
    """Find day.

    Args:
        dayinyear (int): Description.
        month (int): Description.
        isleap (bool): Description.

    Returns:
        int: Description.
    """
    _PREV_MONTH_END_LEAP = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    _PREV_MONTH_END = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    previous_days = _PREV_MONTH_END_LEAP if isleap else _PREV_MONTH_END
    return dayinyear - previous_days[month - 1]

@symbolic_atom(
    witness_lastj2000dayofyear,
    expr=LASTJ2000DAYOFYEAR_EXPR,
    dim_map=LASTJ2000DAYOFYEAR_DIM_MAP,
    variables=LASTJ2000DAYOFYEAR_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
    skip_dim_check=True,
)
@icontract.require(lambda year: year is not None, "year cannot be None")
@icontract.ensure(lambda result: result is not None, "Lastj2000Dayofyear output must not be None")
def lastj2000dayofyear(year: int) -> int:
    """Lastj2000dayofyear.

    Args:
        year (int): Description.

    Returns:
        int: Description.
    """
    return 365 * year + year // 4 - year // 100 + year // 400 - 730120

@symbolic_atom(
    witness_hms2fd,
    expr=HMS2FD_EXPR,
    dim_map=HMS2FD_DIM_MAP,
    constants=TIME_CONSTANTS,
    validity_bounds={
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "s": TIME_OF_DAY_VALIDITY_BOUNDS["s"],
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
    },
    variables=HMS2FD_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda h: h is not None, "h cannot be None")
@icontract.require(lambda m: m is not None, "m cannot be None")
@icontract.require(lambda s: s is not None, "s cannot be None")
@icontract.ensure(lambda result: result is not None, "Hms2Fd output must not be None")
def hms2fd(h: int, m: int, s: float) -> float:
    """Hms2fd.

    Args:
        h (int): Description.
        m (int): Description.
        s (float): Description.

    Returns:
        float: Description.
    """
    return ((60 * (60 * h + m)) + s) / 86400.0

@symbolic_atom(
    witness_fd2hms,
    expr=FD2HMS_EXPR,
    dim_map=FD2HMS_DIM_MAP,
    constants=TIME_CONSTANTS,
    validity_bounds={
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "s": TIME_OF_DAY_VALIDITY_BOUNDS["s"],
    },
    variables=FD2HMS_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda fd: fd is not None, "fd cannot be None")
@icontract.ensure(lambda result: result is not None, "Fd2Hms output must not be None")
def fd2hms(fd: float) -> tuple[int, int, float]:
    """Fd2hms.

    Args:
        fd (float): Description.

    Returns:
        tuple[int, int, float]: Description.
    """
    secinday = fd * 86400.0
    hours = int(secinday // 3600)
    secinday -= 3600 * hours
    mins = int(secinday // 60)
    secinday -= 60 * mins
    return (hours, mins, secinday)

@symbolic_atom(
    witness_fd2hmsf,
    expr=FD2HMSF_EXPR,
    dim_map=FD2HMSF_DIM_MAP,
    constants=TIME_CONSTANTS,
    validity_bounds={
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "sec": TIME_OF_DAY_VALIDITY_BOUNDS["sec"],
        "fsec": TIME_OF_DAY_VALIDITY_BOUNDS["fsec"],
    },
    variables=FD2HMSF_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda fd: fd is not None, "fd cannot be None")
@icontract.ensure(lambda result: result is not None, "Fd2Hmsf output must not be None")
def fd2hmsf(fd: float) -> tuple[int, int, int, float]:
    """Fd2hmsf.

    Args:
        fd (float): Description.

    Returns:
        tuple[int, int, int, float]: Description.
    """
    h, m, sid = fd2hms(fd)
    sec = int(sid // 1)
    fsec = sid - sec
    return (h, m, sec, fsec)

@symbolic_atom(
    witness_cal2jd,
    expr=CAL2JD_EXPR,
    dim_map=CAL2JD_DIM_MAP,
    constants=JD_CONSTANTS,
    validity_bounds={
        "M": CALENDAR_VALIDITY_BOUNDS["M"],
        "D": CALENDAR_VALIDITY_BOUNDS["D"],
    },
    variables=CAL2JD_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda Y: Y is not None, "Y cannot be None")
@icontract.require(lambda M: M is not None, "M cannot be None")
@icontract.require(lambda D: D is not None, "D cannot be None")
@icontract.ensure(lambda result: result is not None, "Cal2Jd output must not be None")
def cal2jd(Y: int, M: int, D: int) -> float:
    """Cal2jd.

    Args:
        Y (int): Description.
        M (int): Description.
        D (int): Description.

    Returns:
        float: Description.
    """
    DJ2000 = 2451545.0
    ly = isleapyear(Y)
    y = Y - 1
    d1 = 365 * y + y // 4 - y // 100 + y // 400 - 730120
    d2 = find_dayinyear(M, D, ly)
    d = d1 + d2
    return (DJ2000, float(d))

@symbolic_atom(
    witness_calhms2jd,
    expr=CALHMS2JD_EXPR,
    dim_map=CALHMS2JD_DIM_MAP,
    constants=JD_CONSTANTS,
    validity_bounds={
        "M": CALENDAR_VALIDITY_BOUNDS["M"],
        "D": CALENDAR_VALIDITY_BOUNDS["D"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "sec": TIME_OF_DAY_VALIDITY_BOUNDS["sec"],
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
    },
    variables=CALHMS2JD_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda Y, M, D: 1 <= M <= 12 and 1 <= D <= 31, "M must be 1-12, D must be 1-31")
@icontract.ensure(lambda result: result is not None, "Calhms2Jd output must not be None")
def calhms2jd(Y: int, M: int, D: int, h: int, m: int, sec: float) -> float:
    """Calhms2jd.

    Args:
        Y (int): Description.
        M (int): Description.
        D (int): Description.
        h (int): Description.
        m (int): Description.
        sec (float): Description.

    Returns:
        float: Description.
    """
    jd1, jd2 = cal2jd(Y, M, D)
    fd = hms2fd(h, m, sec)
    return (jd1, jd2 + fd - 0.5)

@symbolic_atom(
    witness_jd2cal,
    expr=JD2CAL_EXPR,
    dim_map=JD2CAL_DIM_MAP,
    validity_bounds={
        "M": CALENDAR_VALIDITY_BOUNDS["M"],
        "D": CALENDAR_VALIDITY_BOUNDS["D"],
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
    },
    variables=JD2CAL_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda dj1: dj1 is not None, "dj1 cannot be None")
@icontract.require(lambda dj2: dj2 is not None, "dj2 cannot be None")
@icontract.ensure(lambda result: result is not None, "Jd2Cal output must not be None")
def jd2cal(dj1: float, dj2: float) -> tuple[int, int, int, float]:
    """Jd2cal.

    Args:
        dj1 (float): Description.
        dj2 (float): Description.

    Returns:
        tuple[int, int, int, float]: Description.
    """
    d1 = round(dj1)
    d2 = round(dj2)
    jd = d1 + d2
    f1 = float(dj1 - d1)
    f2 = float(dj2 - d2)
    s = 0.5
    cs = 0.0
    for x in (f1, f2):
        t = s + x
        if abs(s) >= abs(x):
            cs += (s - t) + x
        else:
            cs += (x - t) + s
        s = t
        if s >= 1.0:
            jd += 1
            s -= 1.0
    f = s + cs
    cs = f - s
    if f < 0:
        f = s + 1.0
        cs += (1.0 - f) + s
        s = f
        f = s + cs
        cs = f - s
        jd -= 1
    import sys
    eps_f = sys.float_info.epsilon
    if (f - 1.0) >= -eps_f / 4.0:
        t = s - 1.0
        cs += (s - t) - 1.0
        s = t
        f = s + cs
        if -eps_f / 2.0 < f:
            jd += 1
            f = max(f, 0.0)
    ell = int(jd) + 68569
    n = (4 * ell) // 146097
    ell -= (146097 * n + 3) // 4
    i = (4000 * (ell + 1)) // 1461001
    ell -= (1461 * i) // 4 - 31
    k = (80 * ell) // 2447
    D = ell - (2447 * k) // 80
    ell = k // 11
    M = k + 2 - 12 * ell
    Y = 100 * (n - 49) + i + ell
    fd = f
    return (int(Y), int(M), int(D), fd)

@symbolic_atom(
    witness_jd2calhms,
    expr=JD2CALHMS_EXPR,
    dim_map=JD2CALHMS_DIM_MAP,
    validity_bounds={
        "M": CALENDAR_VALIDITY_BOUNDS["M"],
        "D": CALENDAR_VALIDITY_BOUNDS["D"],
        "fd": CALENDAR_VALIDITY_BOUNDS["fd"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "sec": TIME_OF_DAY_VALIDITY_BOUNDS["sec"],
    },
    variables=JD2CALHMS_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda dj1: dj1 is not None, "dj1 cannot be None")
@icontract.require(lambda dj2: dj2 is not None, "dj2 cannot be None")
@icontract.ensure(lambda result: result is not None, "Jd2Calhms output must not be None")
def jd2calhms(dj1: float, dj2: float) -> tuple[int, int, int, int, int, float]:
    """Jd2calhms.

    Args:
        dj1 (float): Description.
        dj2 (float): Description.

    Returns:
        tuple[int, int, int, int, int, float]: Description.
    """
    y, m, d, fd = jd2cal(dj1, dj2)
    h, mn, sec = fd2hms(fd)
    return (y, m, d, h, mn, sec)

@symbolic_atom(
    witness_utc2tai,
    expr=UTC2TAI_EXPR,
    dim_map=UTC2TAI_DIM_MAP,
    constants={"day_seconds": TIME_CONSTANTS["day_seconds"]},
    validity_bounds=LEAP_SECOND_VALIDITY_BOUNDS,
    variables=UTC2TAI_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda utc1: utc1 is not None, "utc1 cannot be None")
@icontract.require(lambda utc2: utc2 is not None, "utc2 cannot be None")
@icontract.ensure(lambda result: result is not None, "Utc2Tai output must not be None")
def utc2tai(utc1: float, utc2: float) -> float:
    """Utc2tai.

    Args:
        utc1 (float): Description.
        utc2 (float): Description.

    Returns:
        float: Description.
    """
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
    big1 = abs(utc1) >= abs(utc2)
    if big1:
        u1, u2 = float(utc1), float(utc2)
    else:
        u1, u2 = float(utc2), float(utc1)
    _, _, _, fd = jd2cal(u1, u2)
    jd2000_day = (u1 - DJ2000) + u2
    idx = bisect.bisect_right(_LEAP_JD2000, jd2000_day) - 1
    dt0 = _LEAP_SECONDS[idx] if idx >= 0 else 0.0
    z2 = u2 - fd
    dt24 = dt0
    fd += (dt24 - dt0) / 86400.0
    a2 = z2 + fd + dt0 / 86400.0
    if big1:
        return (u1, a2)
    return (a2, u1)

@symbolic_atom(
    witness_tai2utc,
    expr=TAI2UTC_EXPR,
    dim_map=TAI2UTC_DIM_MAP,
    constants={"day_seconds": TIME_CONSTANTS["day_seconds"]},
    validity_bounds=LEAP_SECOND_VALIDITY_BOUNDS,
    variables=TAI2UTC_VARIABLES,
    bibliography=TEMPO_CALENDAR_BIBLIOGRAPHY,
)
@icontract.require(lambda tai1: tai1 is not None, "tai1 cannot be None")
@icontract.require(lambda tai2: tai2 is not None, "tai2 cannot be None")
@icontract.ensure(lambda result: result is not None, "Tai2Utc output must not be None")
def tai2utc(tai1: float, tai2: float) -> float:
    """Tai2utc.

    Args:
        tai1 (float): Description.
        tai2 (float): Description.

    Returns:
        float: Description.
    """
    big1 = abs(tai1) >= abs(tai2)
    if big1:
        a1, a2 = float(tai1), float(tai2)
    else:
        a1, a2 = float(tai2), float(tai1)
    u1 = a1
    u2 = a2
    for _ in range(2):
        g1, g2 = utc2tai(u1, u2)
        u2 += a1 - g1
        u2 += a2 - g2
    if big1:
        return (u1, u2)
    return (u2, u1)


"""Auto-generated FFI bindings for julia implementations."""


def _isleapyear_ffi(year: int) -> bool:
    """Wrapper that calls the Julia version of isleapyear. Passes arguments through and returns the result."""
    return jl.eval("isleapyear(year)")

def _find_dayinyear_ffi(month: int, day: int, isleap: bool) -> int:
    """Wrapper that calls the Julia version of find dayinyear. Passes arguments through and returns the result."""
    return jl.eval("find_dayinyear(month, day, isleap)")

def _find_year_ffi(d: float) -> int:
    """Wrapper that calls the Julia version of find year. Passes arguments through and returns the result."""
    return jl.eval("find_year(d)")

def _find_month_ffi(dayinyear: int, isleap: bool) -> int:
    """Wrapper that calls the Julia version of find month. Passes arguments through and returns the result."""
    return jl.eval("find_month(dayinyear, isleap)")

def _find_day_ffi(dayinyear: int, month: int, isleap: bool) -> int:
    """Wrapper that calls the Julia version of find day. Passes arguments through and returns the result."""
    return jl.eval("find_day(dayinyear, month, isleap)")

def _lastj2000dayofyear_ffi(year: int) -> int:
    """Wrapper that calls the Julia version of lastj2000 dayofyear. Passes arguments through and returns the result."""
    return jl.eval("lastj2000dayofyear(year)")

def _hms2fd_ffi(h: int, m: int, s: float) -> float:
    """Wrapper that calls the Julia version of hms2 fd. Passes arguments through and returns the result."""
    return jl.eval("hms2fd(h, m, s)")

def _fd2hms_ffi(fd: float) -> tuple[int, int, float]:
    """Wrapper that calls the Julia version of fd2 hms. Passes arguments through and returns the result."""
    return jl.eval("fd2hms(fd)")

def _fd2hmsf_ffi(fd: float) -> tuple[int, int, int, float]:
    """Wrapper that calls the Julia version of fd2 hmsf. Passes arguments through and returns the result."""
    return jl.eval("fd2hmsf(fd)")

def _cal2jd_ffi(Y: int, M: int, D: int) -> float:
    """Wrapper that calls the Julia version of cal2 jd. Passes arguments through and returns the result."""
    return jl.eval("cal2jd(Y, M, D)")

def _calhms2jd_ffi(Y: int, M: int, D: int, h: int, m: int, sec: float) -> float:
    """Wrapper that calls the Julia version of calhms2 jd. Passes arguments through and returns the result."""
    return jl.eval("calhms2jd(Y, M, D, h, m, sec)")

def _jd2cal_ffi(dj1: float, dj2: float) -> tuple[int, int, int, float]:
    """Wrapper that calls the Julia version of jd2 cal. Passes arguments through and returns the result."""
    return jl.eval("jd2cal(dj1, dj2)")

def _jd2calhms_ffi(dj1: float, dj2: float) -> tuple[int, int, int, int, int, float]:
    """Wrapper that calls the Julia version of jd2 calhms. Passes arguments through and returns the result."""
    return jl.eval("jd2calhms(dj1, dj2)")

def _utc2tai_ffi(utc1: float, utc2: float) -> float:
    """Wrapper that calls the Julia version of utc2 tai. Passes arguments through and returns the result."""
    return jl.eval("utc2tai(utc1, utc2)")

def _tai2utc_ffi(tai1: float, tai2: float) -> float:
    """Wrapper that calls the Julia version of tai2 utc. Passes arguments through and returns the result."""
    return jl.eval("tai2utc(tai1, tai2)")
