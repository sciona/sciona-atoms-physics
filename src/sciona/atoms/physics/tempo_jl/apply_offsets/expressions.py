from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import SECOND


sec, ts1, ts2, result, seconds, offset, zero_offset = sp.symbols(
    "sec ts1 ts2 result seconds offset zero_offset"
)

TEMPO_BIBLIOGRAPHY = [
    "iau2006sofa",
    "repo_tempo_jl",
]

APPLY_OFFSETS_EXPR = sp.Eq(result, sec + ts1 - ts2)
APPLY_OFFSETS_DIM_MAP = {
    "sec": SECOND,
    "ts1": SECOND,
    "ts2": SECOND,
    "result": SECOND,
}
APPLY_OFFSETS_VARIABLES = {
    "sec": "input",
    "ts1": "input",
    "ts2": "input",
    "result": "output",
}

ZERO_OFFSET_EXPR = sp.Eq(offset, zero_offset)
ZERO_OFFSET_DIM_MAP = {
    "seconds": SECOND,
    "offset": SECOND,
    "zero_offset": SECOND,
}
ZERO_OFFSET_VARIABLES = {
    "seconds": "input",
    "offset": "output",
    "zero_offset": "constant",
}
ZERO_OFFSET_CONSTANTS = {
    "zero_offset": 0.0,
}
