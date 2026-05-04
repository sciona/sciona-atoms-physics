"""Symbolic expressions for Tempo.jl calendar and time-scale conversions."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND


year, month, day, dayinyear, isleap = sp.symbols(
    "year month day dayinyear isleap"
)
last_j2000_day, previous_month_day, month_start_day = sp.symbols(
    "last_j2000_day previous_month_day month_start_day"
)
d, h, m, s, fd, sec, fsec, secinday = sp.symbols(
    "d h m s fd sec fsec secinday"
)
Y, M, D = sp.symbols("Y M D")
jd1, jd2, julian_day, j2000_offset_day = sp.symbols(
    "jd1 jd2 julian_day j2000_offset_day"
)
utc1, utc2, tai1, tai2, utc_total, tai_total = sp.symbols(
    "utc1 utc2 tai1 tai2 utc_total tai_total"
)
delta_at, day_seconds, hour_seconds, minute_seconds = sp.symbols(
    "delta_at day_seconds hour_seconds minute_seconds"
)
jd_epoch, half_day = sp.symbols("jd_epoch half_day")
leap_year_flag, leap_year_rule = sp.symbols("leap_year_flag leap_year_rule")

TEMPO_CALENDAR_BIBLIOGRAPHY = [
    "urban2013almanac",
    "repo_tempo_jl",
]

TIME_CONSTANTS = {
    "day_seconds": 86400.0,
    "hour_seconds": 3600.0,
    "minute_seconds": 60.0,
}
JD_CONSTANTS = {
    **TIME_CONSTANTS,
    "jd_epoch": 2451545.0,
    "half_day": 0.5,
}

ISLEAPYEAR_EXPR = sp.Eq(leap_year_flag, leap_year_rule)
ISLEAPYEAR_DIM_MAP = {
    "year": DIMENSIONLESS,
    "leap_year_flag": DIMENSIONLESS,
    "leap_year_rule": DIMENSIONLESS,
}
ISLEAPYEAR_VARIABLES = {
    "year": "input",
    "leap_year_flag": "output",
    "leap_year_rule": "parameter",
}

FIND_DAYINYEAR_EXPR = sp.Eq(dayinyear, previous_month_day + day)
FIND_DAYINYEAR_DIM_MAP = {
    "month": DIMENSIONLESS,
    "day": DIMENSIONLESS,
    "isleap": DIMENSIONLESS,
    "previous_month_day": DIMENSIONLESS,
    "dayinyear": DIMENSIONLESS,
}
FIND_DAYINYEAR_VARIABLES = {
    "month": "input",
    "day": "input",
    "isleap": "parameter",
    "previous_month_day": "parameter",
    "dayinyear": "output",
}

FIND_YEAR_EXPR = sp.Eq(d, last_j2000_day + dayinyear)
FIND_YEAR_DIM_MAP = {
    "d": DIMENSIONLESS,
    "year": DIMENSIONLESS,
    "last_j2000_day": DIMENSIONLESS,
    "dayinyear": DIMENSIONLESS,
}
FIND_YEAR_VARIABLES = {
    "d": "input",
    "year": "output",
    "last_j2000_day": "parameter",
    "dayinyear": "parameter",
}

FIND_MONTH_EXPR = sp.Eq(dayinyear, month_start_day + day)
FIND_MONTH_DIM_MAP = {
    "dayinyear": DIMENSIONLESS,
    "isleap": DIMENSIONLESS,
    "month_start_day": DIMENSIONLESS,
    "day": DIMENSIONLESS,
    "month": DIMENSIONLESS,
}
FIND_MONTH_VARIABLES = {
    "dayinyear": "input",
    "isleap": "parameter",
    "month_start_day": "parameter",
    "day": "parameter",
    "month": "output",
}

FIND_DAY_EXPR = sp.Eq(dayinyear, previous_month_day + day)
FIND_DAY_DIM_MAP = {
    "dayinyear": DIMENSIONLESS,
    "month": DIMENSIONLESS,
    "isleap": DIMENSIONLESS,
    "previous_month_day": DIMENSIONLESS,
    "day": DIMENSIONLESS,
}
FIND_DAY_VARIABLES = {
    "dayinyear": "input",
    "month": "input",
    "isleap": "parameter",
    "previous_month_day": "parameter",
    "day": "output",
}

LASTJ2000DAYOFYEAR_EXPR = sp.Eq(
    last_j2000_day,
    365 * year
    + sp.floor(year / 4)
    - sp.floor(year / 100)
    + sp.floor(year / 400)
    - 730120,
)
LASTJ2000DAYOFYEAR_DIM_MAP = {
    "year": DIMENSIONLESS,
    "last_j2000_day": DIMENSIONLESS,
}
LASTJ2000DAYOFYEAR_VARIABLES = {
    "year": "input",
    "last_j2000_day": "output",
}

HMS2FD_EXPR = sp.Eq(
    fd,
    (hour_seconds * h + minute_seconds * m + s) / day_seconds,
)
HMS2FD_DIM_MAP = {
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "s": SECOND,
    "fd": DIMENSIONLESS,
    "hour_seconds": SECOND,
    "minute_seconds": SECOND,
    "day_seconds": SECOND,
}
HMS2FD_VARIABLES = {
    "h": "input",
    "m": "input",
    "s": "input",
    "fd": "output",
    "hour_seconds": "constant",
    "minute_seconds": "constant",
    "day_seconds": "constant",
}

FD2HMS_EXPR = sp.Eq(
    fd * day_seconds,
    hour_seconds * h + minute_seconds * m + s,
)
FD2HMS_DIM_MAP = HMS2FD_DIM_MAP
FD2HMS_VARIABLES = {
    "fd": "input",
    "h": "output",
    "m": "output",
    "s": "output",
    "hour_seconds": "constant",
    "minute_seconds": "constant",
    "day_seconds": "constant",
}

FD2HMSF_EXPR = sp.Eq(
    fd * day_seconds,
    hour_seconds * h + minute_seconds * m + sec + fsec,
)
FD2HMSF_DIM_MAP = {
    "fd": DIMENSIONLESS,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "sec": SECOND,
    "fsec": SECOND,
    "hour_seconds": SECOND,
    "minute_seconds": SECOND,
    "day_seconds": SECOND,
}
FD2HMSF_VARIABLES = {
    "fd": "input",
    "h": "output",
    "m": "output",
    "sec": "output",
    "fsec": "output",
    "hour_seconds": "constant",
    "minute_seconds": "constant",
    "day_seconds": "constant",
}

CAL2JD_EXPR = sp.Eq(julian_day, jd_epoch + j2000_offset_day)
CAL2JD_DIM_MAP = {
    "Y": DIMENSIONLESS,
    "M": DIMENSIONLESS,
    "D": DIMENSIONLESS,
    "julian_day": DIMENSIONLESS,
    "jd_epoch": DIMENSIONLESS,
    "j2000_offset_day": DIMENSIONLESS,
}
CAL2JD_VARIABLES = {
    "Y": "input",
    "M": "input",
    "D": "input",
    "julian_day": "output",
    "jd_epoch": "constant",
    "j2000_offset_day": "parameter",
}

CALHMS2JD_EXPR = sp.Eq(
    julian_day,
    jd_epoch + j2000_offset_day + fd - half_day,
)
CALHMS2JD_DIM_MAP = {
    **CAL2JD_DIM_MAP,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "sec": SECOND,
    "fd": DIMENSIONLESS,
    "half_day": DIMENSIONLESS,
}
CALHMS2JD_VARIABLES = {
    "Y": "input",
    "M": "input",
    "D": "input",
    "h": "input",
    "m": "input",
    "sec": "input",
    "julian_day": "output",
    "jd_epoch": "constant",
    "half_day": "constant",
    "j2000_offset_day": "parameter",
    "fd": "parameter",
}

JD2CAL_EXPR = sp.Eq(julian_day, jd1 + jd2)
JD2CAL_DIM_MAP = {
    "jd1": DIMENSIONLESS,
    "jd2": DIMENSIONLESS,
    "julian_day": DIMENSIONLESS,
    "Y": DIMENSIONLESS,
    "M": DIMENSIONLESS,
    "D": DIMENSIONLESS,
    "fd": DIMENSIONLESS,
}
JD2CAL_VARIABLES = {
    "jd1": "input",
    "jd2": "input",
    "julian_day": "parameter",
    "Y": "output",
    "M": "output",
    "D": "output",
    "fd": "output",
}

JD2CALHMS_EXPR = sp.Eq(julian_day, jd1 + jd2)
JD2CALHMS_DIM_MAP = {
    **JD2CAL_DIM_MAP,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "sec": SECOND,
}
JD2CALHMS_VARIABLES = {
    "jd1": "input",
    "jd2": "input",
    "julian_day": "parameter",
    "fd": "parameter",
    "Y": "output",
    "M": "output",
    "D": "output",
    "h": "output",
    "m": "output",
    "sec": "output",
}

UTC2TAI_EXPR = sp.Eq(tai_total, utc1 + utc2 + delta_at / day_seconds)
UTC2TAI_DIM_MAP = {
    "utc1": DIMENSIONLESS,
    "utc2": DIMENSIONLESS,
    "tai_total": DIMENSIONLESS,
    "delta_at": SECOND,
    "day_seconds": SECOND,
}
UTC2TAI_VARIABLES = {
    "utc1": "input",
    "utc2": "input",
    "tai_total": "output",
    "delta_at": "parameter",
    "day_seconds": "constant",
}

TAI2UTC_EXPR = sp.Eq(utc_total, tai1 + tai2 - delta_at / day_seconds)
TAI2UTC_DIM_MAP = {
    "tai1": DIMENSIONLESS,
    "tai2": DIMENSIONLESS,
    "utc_total": DIMENSIONLESS,
    "delta_at": SECOND,
    "day_seconds": SECOND,
}
TAI2UTC_VARIABLES = {
    "tai1": "input",
    "tai2": "input",
    "utc_total": "output",
    "delta_at": "parameter",
    "day_seconds": "constant",
}

CALENDAR_VALIDITY_BOUNDS = {
    "month": (1.0, 12.0),
    "day": (1.0, 31.0),
    "M": (1.0, 12.0),
    "D": (1.0, 31.0),
    "dayinyear": (1.0, 366.0),
    "fd": (0.0, 1.0),
}
TIME_OF_DAY_VALIDITY_BOUNDS = {
    "h": (0.0, 23.0),
    "m": (0.0, 59.0),
    "s": (0.0, 61.0),
    "sec": (0.0, 61.0),
    "fsec": (0.0, 1.0),
}
LEAP_SECOND_VALIDITY_BOUNDS = {
    "delta_at": (0.0, None),
    "day_seconds": (1.0, None),
}
