"""Symbolic expressions for top-level Tempo.jl time-scale atoms."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import SECOND


source_time, target_time = sp.symbols("source_time target_time")
duration, integer_duration, fractional_duration = sp.symbols(
    "duration integer_duration fractional_duration"
)

TEMPO_ROOT_BIBLIOGRAPHY = [
    "urban2013almanac",
    "repo_tempo_jl",
]

GRAPH_TIME_SCALE_EXPR = sp.Eq(target_time, source_time)
GRAPH_TIME_SCALE_DIM_MAP = {
    "source_time": SECOND,
    "target_time": SECOND,
}
GRAPH_TIME_SCALE_VARIABLES = {
    "source_time": "input",
    "target_time": "output",
}

HIGH_PRECISION_DURATION_EXPR = sp.Eq(
    duration,
    integer_duration + fractional_duration,
)
HIGH_PRECISION_DURATION_DIM_MAP = {
    "duration": SECOND,
    "integer_duration": SECOND,
    "fractional_duration": SECOND,
}
HIGH_PRECISION_DURATION_VARIABLES = {
    "duration": "input",
    "integer_duration": "output",
    "fractional_duration": "output",
}
HIGH_PRECISION_DURATION_VALIDITY_BOUNDS = {
    "fractional_duration": (0.0, 1.0),
}
