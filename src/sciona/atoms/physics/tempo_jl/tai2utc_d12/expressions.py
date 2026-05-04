from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, SECOND


(
    utc1,
    utc2,
    utc_total,
    tai1,
    tai2,
    tai_total,
    tai_estimate,
    candidate_utc,
    delta_at,
    day_seconds,
) = sp.symbols(
    "utc1 utc2 utc_total tai1 tai2 tai_total tai_estimate candidate_utc "
    "delta_at day_seconds"
)


TAI2UTC_D12_BIBLIOGRAPHY = [
    "iau2006sofa",
    "repo_tempo_jl",
]

DAY_SECONDS_CONSTANT = 86400.0

UTC_TO_TAI_EXPR = sp.Eq(tai_total, utc1 + utc2 + delta_at / day_seconds)
UTC_TO_TAI_DIM_MAP = {
    "utc1": SECOND,
    "utc2": SECOND,
    "tai1": SECOND,
    "tai2": SECOND,
    "tai_total": SECOND,
    "delta_at": SECOND,
    "day_seconds": DIMENSIONLESS,
}
UTC_TO_TAI_VARIABLES = {
    "utc1": "input",
    "utc2": "input",
    "tai1": "output",
    "tai2": "output",
    "tai_total": "output",
    "delta_at": "parameter",
    "day_seconds": "constant",
}
UTC_TO_TAI_CONSTANTS = {
    "day_seconds": DAY_SECONDS_CONSTANT,
}
UTC_TO_TAI_VALIDITY_BOUNDS = {
    "delta_at": (0.0, None),
    "day_seconds": (1.0, None),
}

TAI_TO_UTC_EXPR = sp.Eq(candidate_utc, tai1 + tai2 - delta_at / day_seconds)
TAI_TO_UTC_DIM_MAP = {
    "tai1": SECOND,
    "tai2": SECOND,
    "tai_estimate": SECOND,
    "utc1": SECOND,
    "utc2": SECOND,
    "candidate_utc": SECOND,
    "delta_at": SECOND,
    "day_seconds": DIMENSIONLESS,
}
TAI_TO_UTC_VARIABLES = {
    "tai1": "input",
    "tai2": "input",
    "tai_estimate": "input",
    "utc1": "output",
    "utc2": "output",
    "candidate_utc": "output",
    "delta_at": "parameter",
    "day_seconds": "constant",
}
TAI_TO_UTC_CONSTANTS = {
    "day_seconds": DAY_SECONDS_CONSTANT,
}
TAI_TO_UTC_VALIDITY_BOUNDS = {
    "delta_at": (0.0, None),
    "day_seconds": (1.0, None),
}
