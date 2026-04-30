from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND


(
    seconds,
    offset,
    k,
    eb,
    m0,
    m1,
    century_to_seconds,
    a1,
    w1,
    p1,
    a2,
    w2,
    p2,
    a3,
    w3,
    p3,
    a4,
    w4,
    p4,
    a5,
    w5,
    p5,
    a6,
    w6,
    p6,
    a7,
    p7,
) = sp.symbols(
    "seconds offset k eb m0 m1 century_to_seconds "
    "a1 w1 p1 a2 w2 p2 a3 w3 p3 a4 w4 p4 a5 w5 p5 a6 w6 p6 a7 p7"
)

TEMPO_OFFSET_BIBLIOGRAPHY = [
    "iau2006sofa",
    "repo_tempo_jl",
]

LOW_ORDER_TT2TDB_EXPR = sp.Eq(
    offset,
    k * sp.sin(m0 + m1 * seconds + eb * sp.sin(m0 + m1 * seconds)),
)
LOW_ORDER_TT2TDB_DIM_MAP = {
    "seconds": SECOND,
    "offset": SECOND,
    "k": SECOND,
    "eb": DIMENSIONLESS,
    "m0": DIMENSIONLESS,
    "m1": SECOND.power(-1),
}
LOW_ORDER_TT2TDB_VARIABLES = {
    "seconds": "input",
    "offset": "output",
    "k": "constant",
    "eb": "constant",
    "m0": "constant",
    "m1": "constant",
}
LOW_ORDER_TT2TDB_CONSTANTS = {
    "k": 1.657e-3,
    "eb": 1.671e-2,
    "m0": 6.239996,
    "m1": 1.99096871e-7,
}

centuries = seconds / century_to_seconds

HIGH_ORDER_TT2TDB_EXPR = sp.Eq(
    offset,
    a1 * sp.sin(w1 * centuries + p1)
    + a2 * sp.sin(w2 * centuries + p2)
    + a3 * sp.sin(w3 * centuries + p3)
    + a4 * sp.sin(w4 * centuries + p4)
    + a5 * sp.sin(w5 * centuries + p5)
    + a6 * sp.sin(w6 * centuries + p6)
    + a7 * centuries * sp.sin(w1 * centuries + p7),
)
HIGH_ORDER_TT2TDB_DIM_MAP = {
    "seconds": SECOND,
    "century_to_seconds": SECOND,
    "offset": SECOND,
    "a1": SECOND,
    "w1": DIMENSIONLESS,
    "p1": DIMENSIONLESS,
    "a2": SECOND,
    "w2": DIMENSIONLESS,
    "p2": DIMENSIONLESS,
    "a3": SECOND,
    "w3": DIMENSIONLESS,
    "p3": DIMENSIONLESS,
    "a4": SECOND,
    "w4": DIMENSIONLESS,
    "p4": DIMENSIONLESS,
    "a5": SECOND,
    "w5": DIMENSIONLESS,
    "p5": DIMENSIONLESS,
    "a6": SECOND,
    "w6": DIMENSIONLESS,
    "p6": DIMENSIONLESS,
    "a7": SECOND,
    "p7": DIMENSIONLESS,
}
HIGH_ORDER_TT2TDB_VARIABLES = {
    "seconds": "input",
    "century_to_seconds": "constant",
    "offset": "output",
    "a1": "constant",
    "w1": "constant",
    "p1": "constant",
    "a2": "constant",
    "w2": "constant",
    "p2": "constant",
    "a3": "constant",
    "w3": "constant",
    "p3": "constant",
    "a4": "constant",
    "w4": "constant",
    "p4": "constant",
    "a5": "constant",
    "w5": "constant",
    "p5": "constant",
    "a6": "constant",
    "w6": "constant",
    "p6": "constant",
    "a7": "constant",
    "p7": "constant",
}
HIGH_ORDER_TT2TDB_CONSTANTS = {
    "century_to_seconds": 86400.0 * 36525.0,
    "a1": 0.001657,
    "w1": 628.3076,
    "p1": 6.2401,
    "a2": 0.000022,
    "w2": 575.3385,
    "p2": 4.2970,
    "a3": 0.000014,
    "w3": 1256.6152,
    "p3": 6.1969,
    "a4": 0.000005,
    "w4": 606.9777,
    "p4": 4.0212,
    "a5": 0.000005,
    "w5": 52.9691,
    "p5": 0.4444,
    "a6": 0.000002,
    "w6": 21.3299,
    "p6": 5.5431,
    "a7": 0.000010,
    "p7": 4.2490,
}
