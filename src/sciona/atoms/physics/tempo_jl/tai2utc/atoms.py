from __future__ import annotations
"""Auto-generated atom wrappers following the ageoa pattern."""


import numpy as np

import icontract
from ageoa.ghost.registry import register_atom
from .witnesses import witness_cal2jd, witness_calhms2jd, witness_fd2hms, witness_fd2hmsf, witness_find_day, witness_find_dayinyear, witness_find_month, witness_find_year, witness_hms2fd, witness_isleapyear, witness_jd2cal, witness_jd2calhms, witness_lastj2000dayofyear, witness_tai2utc, witness_utc2tai

from juliacall import Main as jl


# Witness functions should be imported from the generated witnesses module

@register_atom(witness_isleapyear)
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

@register_atom(witness_find_dayinyear)
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

@register_atom(witness_find_year)
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

@register_atom(witness_find_month)
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

@register_atom(witness_find_day)
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

@register_atom(witness_lastj2000dayofyear)
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

@register_atom(witness_hms2fd)
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

@register_atom(witness_fd2hms)
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

@register_atom(witness_fd2hmsf)
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

@register_atom(witness_cal2jd)
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

@register_atom(witness_calhms2jd)
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

@register_atom(witness_jd2cal)
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
    l = int(jd) + 68569
    n = (4 * l) // 146097
    l -= (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l -= (1461 * i) // 4 - 31
    k = (80 * l) // 2447
    D = l - (2447 * k) // 80
    l = k // 11
    M = k + 2 - 12 * l
    Y = 100 * (n - 49) + i + l
    fd = f
    return (int(Y), int(M), int(D), fd)

@register_atom(witness_jd2calhms)
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

@register_atom(witness_utc2tai)
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

@register_atom(witness_tai2utc)
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


from juliacall import Main as jl


def _isleapyear_ffi(year):
    """Wrapper that calls the Julia version of isleapyear. Passes arguments through and returns the result."""
    return jl.eval("isleapyear(year)")

def _find_dayinyear_ffi(month, day, isleap):
    """Wrapper that calls the Julia version of find dayinyear. Passes arguments through and returns the result."""
    return jl.eval("find_dayinyear(month, day, isleap)")

def _find_year_ffi(d):
    """Wrapper that calls the Julia version of find year. Passes arguments through and returns the result."""
    return jl.eval("find_year(d)")

def _find_month_ffi(dayinyear, isleap):
    """Wrapper that calls the Julia version of find month. Passes arguments through and returns the result."""
    return jl.eval("find_month(dayinyear, isleap)")

def _find_day_ffi(dayinyear, month, isleap):
    """Wrapper that calls the Julia version of find day. Passes arguments through and returns the result."""
    return jl.eval("find_day(dayinyear, month, isleap)")

def _lastj2000dayofyear_ffi(year):
    """Wrapper that calls the Julia version of lastj2000 dayofyear. Passes arguments through and returns the result."""
    return jl.eval("lastj2000dayofyear(year)")

def _hms2fd_ffi(h, m, s):
    """Wrapper that calls the Julia version of hms2 fd. Passes arguments through and returns the result."""
    return jl.eval("hms2fd(h, m, s)")

def _fd2hms_ffi(fd):
    """Wrapper that calls the Julia version of fd2 hms. Passes arguments through and returns the result."""
    return jl.eval("fd2hms(fd)")

def _fd2hmsf_ffi(fd):
    """Wrapper that calls the Julia version of fd2 hmsf. Passes arguments through and returns the result."""
    return jl.eval("fd2hmsf(fd)")

def _cal2jd_ffi(Y, M, D):
    """Wrapper that calls the Julia version of cal2 jd. Passes arguments through and returns the result."""
    return jl.eval("cal2jd(Y, M, D)")

def _calhms2jd_ffi(Y, M, D, h, m, sec):
    """Wrapper that calls the Julia version of calhms2 jd. Passes arguments through and returns the result."""
    return jl.eval("calhms2jd(Y, M, D, h, m, sec)")

def _jd2cal_ffi(dj1, dj2):
    """Wrapper that calls the Julia version of jd2 cal. Passes arguments through and returns the result."""
    return jl.eval("jd2cal(dj1, dj2)")

def _jd2calhms_ffi(dj1, dj2):
    """Wrapper that calls the Julia version of jd2 calhms. Passes arguments through and returns the result."""
    return jl.eval("jd2calhms(dj1, dj2)")

def _utc2tai_ffi(utc1, utc2):
    """Wrapper that calls the Julia version of utc2 tai. Passes arguments through and returns the result."""
    return jl.eval("utc2tai(utc1, utc2)")

def _tai2utc_ffi(tai1, tai2):
    """Wrapper that calls the Julia version of tai2 utc. Passes arguments through and returns the result."""
    return jl.eval("tai2utc(tai1, tai2)")
