"""Auto-generated atom wrappers following the sciona pattern."""

from __future__ import annotations


import icontract
from sciona.ghost.decorators import symbolic_atom
from sciona.ghost.registry import register_atom

from .expressions import (
    CALENDAR_VALIDITY_BOUNDS,
    DATE_FROM_OFFSET_DIM_MAP,
    DATE_FROM_OFFSET_EXPR,
    DATE_FROM_OFFSET_VARIABLES,
    DATE_FROM_YEAR_DAYINYEAR_DIM_MAP,
    DATE_FROM_YEAR_DAYINYEAR_EXPR,
    DATE_FROM_YEAR_DAYINYEAR_VARIABLES,
    DATETIME_FROM_SECONDS_DIM_MAP,
    DATETIME_FROM_SECONDS_EXPR,
    DATETIME_FROM_SECONDS_VARIABLES,
    JD_SECONDS_CONSTANTS,
    TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
    TIME_CONSTANTS,
    TIME_FROM_SECONDINDAY_DIM_MAP,
    TIME_FROM_SECONDINDAY_EXPR,
    TIME_FROM_SECONDINDAY_FRACTION_DIM_MAP,
    TIME_FROM_SECONDINDAY_FRACTION_EXPR,
    TIME_FROM_SECONDINDAY_FRACTION_VARIABLES,
    TIME_FROM_SECONDINDAY_VARIABLES,
    TIME_OF_DAY_VALIDITY_BOUNDS,
)
from .witnesses import witness_date, witness_datetime, witness_show, witness_time
from juliacall import Main as jl


# Witness functions should be imported from the generated witnesses module

@symbolic_atom(
    witness_date,
    name="date_from_offset",
    expr=DATE_FROM_OFFSET_EXPR,
    dim_map=DATE_FROM_OFFSET_DIM_MAP,
    validity_bounds={
        "month": CALENDAR_VALIDITY_BOUNDS["month"],
        "day": CALENDAR_VALIDITY_BOUNDS["day"],
    },
    variables=DATE_FROM_OFFSET_VARIABLES,
    bibliography=TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
)
@icontract.require(lambda offset: offset is not None, "offset cannot be None")
@icontract.ensure(lambda result: result is not None, "Date output must not be None")
def date(offset: int) -> tuple[int, int, int]:
    """Date.

    Args:
        offset (int): Description.

    Returns:
        tuple[int, int, int]: Description.
    """
    _PREV_MONTH_END_LEAP = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    _PREV_MONTH_END = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

    def _lastj2000(y):
        return 365 * y + y // 4 - y // 100 + y // 400 - 730120

    def _isleap(y):
        return y % 4 == 0 and (y % 400 == 0 or y % 100 != 0)

    def _find_month(diy, leap):
        off = 313 if leap else 323
        return 1 if diy < 32 else (10 * diy + off) // 306

    j2d = int(offset)
    year = (400 * j2d + 292194288) // 146097
    if j2d <= _lastj2000(year - 1):
        year -= 1
    dayinyear = j2d - _lastj2000(year - 1)
    ly = _isleap(year)
    month = _find_month(dayinyear, ly)
    prev = _PREV_MONTH_END_LEAP if ly else _PREV_MONTH_END
    day = dayinyear - prev[month - 1]
    return (year, month, day)

date_from_offset = date

@symbolic_atom(
    witness_date,
    name="date_from_year_dayinyear",
    expr=DATE_FROM_YEAR_DAYINYEAR_EXPR,
    dim_map=DATE_FROM_YEAR_DAYINYEAR_DIM_MAP,
    validity_bounds={
        "dayinyear": CALENDAR_VALIDITY_BOUNDS["dayinyear"],
        "month": CALENDAR_VALIDITY_BOUNDS["month"],
        "day": CALENDAR_VALIDITY_BOUNDS["day"],
    },
    variables=DATE_FROM_YEAR_DAYINYEAR_VARIABLES,
    bibliography=TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
)
@icontract.require(lambda year: year is not None, "year cannot be None")
@icontract.require(lambda dayinyear: dayinyear is not None, "dayinyear cannot be None")
@icontract.ensure(lambda result: result is not None, "Date output must not be None")
def date(year: int, dayinyear: int) -> tuple[int, int, int]:
    """Date.

    Args:
        year (int): Description.
        dayinyear (int): Description.

    Returns:
        tuple[int, int, int]: Description.
    """
    _PREV_MONTH_END_LEAP = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    _PREV_MONTH_END = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    ly = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    off = 313 if ly else 323
    month = 1 if dayinyear < 32 else (10 * dayinyear + off) // 306
    prev = _PREV_MONTH_END_LEAP if ly else _PREV_MONTH_END
    day = dayinyear - prev[month - 1]
    return (year, month, day)

date_from_year_dayinyear = date

@register_atom(witness_show, name="show_date")
@icontract.require(lambda io: io is not None, "io cannot be None")
@icontract.require(lambda d: d is not None, "d cannot be None")
@icontract.ensure(lambda result: result is not None, "Show output must not be None")
def show(io: str, d: str) -> str:
    """Show.

    Args:
        io (str): Description.
        d (str): Description.

    Returns:
        str: Description.
    """
    return str(d)

show_date = show

@register_atom(witness_time, name="time_from_hms")
@icontract.require(lambda hour: hour is not None, "hour cannot be None")
@icontract.require(lambda minute: minute is not None, "minute cannot be None")
@icontract.require(lambda second: second is not None, "second cannot be None")
@icontract.ensure(lambda result: result is not None, "Time output must not be None")
def time(hour: int, minute: int, second: float) -> tuple[int, int, float]:
    """Time.

    Args:
        hour (int): Description.
        minute (int): Description.
        second (float): Description.

    Returns:
        tuple[int, int, float]: Description.
    """
    return (hour, minute, second)

time_from_hms = time

@symbolic_atom(
    witness_time,
    name="time_from_secondinday_fraction",
    expr=TIME_FROM_SECONDINDAY_FRACTION_EXPR,
    dim_map=TIME_FROM_SECONDINDAY_FRACTION_DIM_MAP,
    validity_bounds={
        "secondinday": TIME_OF_DAY_VALIDITY_BOUNDS["secondinday"],
        "fraction": TIME_OF_DAY_VALIDITY_BOUNDS["fraction"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "s": TIME_OF_DAY_VALIDITY_BOUNDS["s"],
    },
    constants={
        "hour_seconds": TIME_CONSTANTS["hour_seconds"],
        "minute_seconds": TIME_CONSTANTS["minute_seconds"],
    },
    variables=TIME_FROM_SECONDINDAY_FRACTION_VARIABLES,
    bibliography=TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
)
@icontract.require(lambda secondinday: secondinday is not None, "secondinday cannot be None")
@icontract.require(lambda fraction: fraction is not None, "fraction cannot be None")
@icontract.ensure(lambda result: result is not None, "Time output must not be None")
def time(secondinday: int, fraction: float) -> tuple[int, int, float]:
    """Time.

    Args:
        secondinday (int): Description.
        fraction (float): Description.

    Returns:
        tuple[int, int, float]: Description.
    """
    sid = int(secondinday)
    hour = sid // 3600
    sid -= 3600 * hour
    minute = sid // 60
    sid -= 60 * minute
    return (hour, minute, float(sid) + fraction)

time_from_secondinday_fraction = time

@symbolic_atom(
    witness_time,
    name="time_from_secondinday",
    expr=TIME_FROM_SECONDINDAY_EXPR,
    dim_map=TIME_FROM_SECONDINDAY_DIM_MAP,
    validity_bounds={
        "secondinday": TIME_OF_DAY_VALIDITY_BOUNDS["secondinday"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "s": TIME_OF_DAY_VALIDITY_BOUNDS["s"],
    },
    constants={
        "hour_seconds": TIME_CONSTANTS["hour_seconds"],
        "minute_seconds": TIME_CONSTANTS["minute_seconds"],
    },
    variables=TIME_FROM_SECONDINDAY_VARIABLES,
    bibliography=TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
)
@icontract.require(lambda secondinday: secondinday is not None, "secondinday cannot be None")
@icontract.ensure(lambda result: result is not None, "Time output must not be None")
def time(secondinday: int) -> tuple[int, int, float]:
    """Time.

    Args:
        secondinday (int): Description.

    Returns:
        tuple[int, int, float]: Description.
    """
    sec = int(secondinday)
    frac = float(secondinday) - sec
    hour = sec // 3600
    sec -= 3600 * hour
    minute = sec // 60
    sec -= 60 * minute
    return (hour, minute, float(sec) + frac)

time_from_secondinday = time

@register_atom(witness_show, name="show_time")
@icontract.require(lambda io: io is not None, "io cannot be None")
@icontract.require(lambda t: t is not None, "t cannot be None")
@icontract.ensure(lambda result: result is not None, "Show output must not be None")
def show(io: str, t: str) -> str:
    """Show.

    Args:
        io (str): Description.
        t (str): Description.

    Returns:
        str: Description.
    """
    return str(t)

show_time = show

@register_atom(witness_datetime, name="datetime_from_components")
@icontract.require(lambda year, month, day: 1 <= month <= 12 and 1 <= day <= 31, "month must be 1-12, day must be 1-31")
@icontract.ensure(lambda result: result is not None, "Datetime output must not be None")
def datetime(year: int, month: int, day: int, hour: int, min: int, sec: float) -> tuple[int, int, int, int, int, float]:
    """Datetime.

    Args:
        year (int): Description.
        month (int): Description.
        day (int): Description.
        hour (int): Description.
        min (int): Description.
        sec (float): Description.

    Returns:
        tuple[int, int, int, int, int, float]: Description.
    """
    return (year, month, day, hour, min, sec)

datetime_from_components = datetime

@register_atom(witness_datetime, name="datetime_from_string")
@icontract.require(lambda s: s is not None, "s cannot be None")
@icontract.ensure(lambda result: result is not None, "Datetime output must not be None")
def datetime(s: str) -> tuple[int, int, int, int, int, float]:
    """Datetime.

    Args:
        s (str): Description.

    Returns:
        tuple[int, int, int, int, int, float]: Description.
    """
    import re as _re
    parts = _re.split(r'[-T:]', s.strip())
    dy = int(parts[0]) if len(parts) > 0 else 2000
    dm = int(parts[1]) if len(parts) > 1 else 1
    dd = int(parts[2]) if len(parts) > 2 else 1
    th = int(parts[3]) if len(parts) > 3 else 0
    tm = int(parts[4]) if len(parts) > 4 else 0
    ts = float(parts[5]) if len(parts) > 5 else 0.0
    return (dy, dm, dd, th, tm, ts)

datetime_from_string = datetime

@symbolic_atom(
    witness_datetime,
    name="datetime_from_seconds",
    expr=DATETIME_FROM_SECONDS_EXPR,
    dim_map=DATETIME_FROM_SECONDS_DIM_MAP,
    validity_bounds={
        "M": CALENDAR_VALIDITY_BOUNDS["M"],
        "D": CALENDAR_VALIDITY_BOUNDS["D"],
        "h": TIME_OF_DAY_VALIDITY_BOUNDS["h"],
        "m": TIME_OF_DAY_VALIDITY_BOUNDS["m"],
        "s": TIME_OF_DAY_VALIDITY_BOUNDS["s"],
    },
    constants=JD_SECONDS_CONSTANTS,
    variables=DATETIME_FROM_SECONDS_VARIABLES,
    bibliography=TEMPO_CONSTRUCTOR_BIBLIOGRAPHY,
)
@icontract.require(lambda seconds: seconds is not None, "seconds cannot be None")
@icontract.ensure(lambda result: result is not None, "Datetime output must not be None")
def datetime(seconds: float) -> tuple[int, int, int, int, int, float]:
    """Datetime.

    Args:
        seconds (float): Description.

    Returns:
        tuple[int, int, int, int, int, float]: Description.
    """
    import sys as _sys
    DJ2000 = 2451545.0
    DAY2SEC = 86400.0
    dj1, dj2 = DJ2000, seconds / DAY2SEC

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
    eps_f = _sys.float_info.epsilon
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

    secinday = fd * DAY2SEC
    hours = int(secinday // 3600)
    secinday -= 3600 * hours
    mins = int(secinday // 60)
    secinday -= 60 * mins
    return (int(Y), int(M), int(D), hours, mins, secinday)

datetime_from_seconds = datetime


"""Auto-generated FFI bindings for julia implementations."""


def _date_ffi(offset):
    """Wrapper that calls the Julia version of date. Passes arguments through and returns the result."""
    return jl.eval("date(offset)")

def _date_ffi(year, dayinyear):
    """Wrapper that calls the Julia version of date. Passes arguments through and returns the result."""
    return jl.eval("date(year, dayinyear)")

def _show_ffi(io, d):
    """Wrapper that calls the Julia version of show. Passes arguments through and returns the result."""
    return jl.eval("show(io, d)")

def _time_ffi(hour, minute, second):
    """Wrapper that calls the Julia version of time. Passes arguments through and returns the result."""
    return jl.eval("time(hour, minute, second)")

def _time_ffi(secondinday, fraction):
    """Wrapper that calls the Julia version of time. Passes arguments through and returns the result."""
    return jl.eval("time(secondinday, fraction)")

def _time_ffi(secondinday):
    """Wrapper that calls the Julia version of time. Passes arguments through and returns the result."""
    return jl.eval("time(secondinday)")

def _show_ffi(io, t):
    """Wrapper that calls the Julia version of show. Passes arguments through and returns the result."""
    return jl.eval("show(io, t)")

def _datetime_ffi(year, month, day, hour, min, sec):
    """Wrapper that calls the Julia version of datetime. Passes arguments through and returns the result."""
    return jl.eval("datetime(year, month, day, hour, min, sec)")

def _datetime_ffi(s):
    """Wrapper that calls the Julia version of datetime. Passes arguments through and returns the result."""
    return jl.eval("datetime(s)")

def _datetime_ffi(seconds):
    """Wrapper that calls the Julia version of datetime. Passes arguments through and returns the result."""
    return jl.eval("datetime(seconds)")
