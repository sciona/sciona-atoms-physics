"""Symbolic expressions for Tempo.jl date/time constructor arithmetic."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND


offset, year, month, day, dayinyear = sp.symbols(
    "offset year month day dayinyear"
)
previous_month_day, last_j2000_day = sp.symbols(
    "previous_month_day last_j2000_day"
)
secondinday, fraction, h, m, s = sp.symbols(
    "secondinday fraction h m s"
)
seconds, julian_day, jd_epoch, day_seconds = sp.symbols(
    "seconds julian_day jd_epoch day_seconds"
)
hour_seconds, minute_seconds = sp.symbols("hour_seconds minute_seconds")
Y, M, D = sp.symbols("Y M D")

TEMPO_CONSTRUCTOR_BIBLIOGRAPHY = [
    "urban2013almanac",
    "repo_tempo_jl",
]

TIME_CONSTANTS = {
    "day_seconds": 86400.0,
    "hour_seconds": 3600.0,
    "minute_seconds": 60.0,
}
JD_SECONDS_CONSTANTS = {
    "day_seconds": 86400.0,
    "jd_epoch": 2451545.0,
}

DATE_FROM_OFFSET_EXPR = sp.Eq(
    offset,
    last_j2000_day + previous_month_day + day,
)
DATE_FROM_OFFSET_DIM_MAP = {
    "offset": DIMENSIONLESS,
    "year": DIMENSIONLESS,
    "month": DIMENSIONLESS,
    "day": DIMENSIONLESS,
    "last_j2000_day": DIMENSIONLESS,
    "previous_month_day": DIMENSIONLESS,
}
DATE_FROM_OFFSET_VARIABLES = {
    "offset": "input",
    "year": "output",
    "month": "output",
    "day": "output",
    "last_j2000_day": "parameter",
    "previous_month_day": "parameter",
}

DATE_FROM_YEAR_DAYINYEAR_EXPR = sp.Eq(dayinyear, previous_month_day + day)
DATE_FROM_YEAR_DAYINYEAR_DIM_MAP = {
    "year": DIMENSIONLESS,
    "dayinyear": DIMENSIONLESS,
    "month": DIMENSIONLESS,
    "day": DIMENSIONLESS,
    "previous_month_day": DIMENSIONLESS,
}
DATE_FROM_YEAR_DAYINYEAR_VARIABLES = {
    "year": "input",
    "dayinyear": "input",
    "month": "output",
    "day": "output",
    "previous_month_day": "parameter",
}

TIME_FROM_SECONDINDAY_FRACTION_EXPR = sp.Eq(
    secondinday + fraction,
    hour_seconds * h + minute_seconds * m + s,
)
TIME_FROM_SECONDINDAY_FRACTION_DIM_MAP = {
    "secondinday": SECOND,
    "fraction": SECOND,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "s": SECOND,
    "hour_seconds": SECOND,
    "minute_seconds": SECOND,
}
TIME_FROM_SECONDINDAY_FRACTION_VARIABLES = {
    "secondinday": "input",
    "fraction": "input",
    "h": "output",
    "m": "output",
    "s": "output",
    "hour_seconds": "constant",
    "minute_seconds": "constant",
}

TIME_FROM_SECONDINDAY_EXPR = sp.Eq(
    secondinday,
    hour_seconds * h + minute_seconds * m + s,
)
TIME_FROM_SECONDINDAY_DIM_MAP = {
    "secondinday": SECOND,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "s": SECOND,
    "hour_seconds": SECOND,
    "minute_seconds": SECOND,
}
TIME_FROM_SECONDINDAY_VARIABLES = {
    "secondinday": "input",
    "h": "output",
    "m": "output",
    "s": "output",
    "hour_seconds": "constant",
    "minute_seconds": "constant",
}

DATETIME_FROM_SECONDS_EXPR = sp.Eq(
    julian_day,
    jd_epoch + seconds / day_seconds,
)
DATETIME_FROM_SECONDS_DIM_MAP = {
    "seconds": SECOND,
    "julian_day": DIMENSIONLESS,
    "jd_epoch": DIMENSIONLESS,
    "day_seconds": SECOND,
    "Y": DIMENSIONLESS,
    "M": DIMENSIONLESS,
    "D": DIMENSIONLESS,
    "h": DIMENSIONLESS,
    "m": DIMENSIONLESS,
    "s": SECOND,
}
DATETIME_FROM_SECONDS_VARIABLES = {
    "seconds": "input",
    "julian_day": "parameter",
    "jd_epoch": "constant",
    "day_seconds": "constant",
    "Y": "output",
    "M": "output",
    "D": "output",
    "h": "output",
    "m": "output",
    "s": "output",
}

CALENDAR_VALIDITY_BOUNDS = {
    "month": (1.0, 12.0),
    "day": (1.0, 31.0),
    "dayinyear": (1.0, 366.0),
    "M": (1.0, 12.0),
    "D": (1.0, 31.0),
}
TIME_OF_DAY_VALIDITY_BOUNDS = {
    "secondinday": (0.0, 86400.0),
    "fraction": (0.0, 1.0),
    "h": (0.0, 23.0),
    "m": (0.0, 59.0),
    "s": (0.0, 61.0),
}
