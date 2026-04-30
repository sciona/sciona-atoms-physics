"""Symbolic scalar relations for helix-geometry atoms.

The heavy atoms in this package are vectorized TrackML geometry routines.
These expressions capture the scalar geometric invariants that are stable
across each vector element; branch handling and Newton iteration remain in
the runtime implementations.
"""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, METER, DimensionalSignature

LENGTH = METER
ANGLE = DIMENSIONLESS
COUNT = DIMENSIONLESS
AREA = DimensionalSignature(L=2)
CURVATURE = DimensionalSignature(L=-1)

(
    x1,
    y1,
    z1,
    x2,
    y2,
    z2,
    x3,
    y3,
    z3,
    x,
    y,
    z,
    x0,
    y0,
    z0,
    xm,
    ym,
    r,
    hel_xm,
    hel_ym,
    hel_r,
    hel_pitch,
    zero_pitch,
    phid,
    dz,
    hel_p,
    hel_dz,
    dist,
    loss,
    large_radius,
    iterations,
    sum_z,
    sum_phi,
    sum_zphi,
    sum_phisqr,
) = sp.symbols(
    "x1 y1 z1 x2 y2 z2 x3 y3 z3 x y z x0 y0 z0 "
    "xm ym r hel_xm hel_ym hel_r hel_pitch zero_pitch phid dz hel_p "
    "hel_dz dist loss large_radius iterations sum_z sum_phi sum_zphi sum_phisqr"
)


HELIX_GEOMETRY_BIBLIOGRAPHY = ["steiner2018trackml", "amrouche2019trackml"]

POINT2D_DIM_MAP = {
    "x1": LENGTH,
    "y1": LENGTH,
    "x2": LENGTH,
    "y2": LENGTH,
    "x3": LENGTH,
    "y3": LENGTH,
}
POINT3D_DIM_MAP = {
    **POINT2D_DIM_MAP,
    "z1": LENGTH,
    "z2": LENGTH,
    "z3": LENGTH,
}
HELIX_CENTER_DIM_MAP = {
    "hel_xm": LENGTH,
    "hel_ym": LENGTH,
}

CIRCLE_RADIUS_EXPR = sp.Eq(r**2, (x1 - xm) ** 2 + (y1 - ym) ** 2)
CIRCLE_DIM_MAP = {
    **POINT2D_DIM_MAP,
    "xm": LENGTH,
    "ym": LENGTH,
    "r": LENGTH,
    "large_radius": LENGTH,
}
CIRCLE_VARIABLES = {
    **{name: "input" for name in POINT2D_DIM_MAP},
    "large_radius": "parameter",
    "xm": "output",
    "ym": "output",
    "r": "output",
}
CIRCLE_VALIDITY_BOUNDS = {
    "r": (0.0, None),
    "large_radius": (0.0, None),
}

PITCH_FROM_TWO_POINTS_EXPR = sp.Eq(hel_pitch, 2 * sp.pi * dz / phid)
PITCH_FROM_TWO_POINTS_DIM_MAP = {
    **POINT3D_DIM_MAP,
    **HELIX_CENTER_DIM_MAP,
    "hel_pitch": LENGTH,
    "phid": ANGLE,
    "dz": LENGTH,
    "zero_pitch": LENGTH,
}
PITCH_FROM_TWO_POINTS_VARIABLES = {
    **{name: "input" for name in POINT3D_DIM_MAP},
    **{name: "input" for name in HELIX_CENTER_DIM_MAP},
    "zero_pitch": "parameter",
    "hel_pitch": "output",
    "phid": "output",
    "dz": "output",
}
PITCH_FROM_TWO_POINTS_VALIDITY_BOUNDS = {
    "phid": (-float(sp.pi), float(sp.pi)),
    "zero_pitch": (0.0, None),
}

# Core slope relation after phase unwrapping and aggregate construction.
LEAST_SQUARES_PITCH_EXPR = sp.Eq(
    hel_pitch,
    2 * sp.pi * (3 * sum_zphi - sum_z * sum_phi) / (3 * sum_phisqr - sum_phi**2),
)
LEAST_SQUARES_PITCH_DIM_MAP = {
    **POINT3D_DIM_MAP,
    **HELIX_CENTER_DIM_MAP,
    "hel_pitch": LENGTH,
    "phid": ANGLE,
    "dz": LENGTH,
    "loss": AREA,
    "zero_pitch": LENGTH,
    "sum_z": LENGTH,
    "sum_phi": ANGLE,
    "sum_zphi": LENGTH,
    "sum_phisqr": ANGLE,
}
LEAST_SQUARES_PITCH_VARIABLES = {
    **{name: "input" for name in POINT3D_DIM_MAP},
    **{name: "input" for name in HELIX_CENTER_DIM_MAP},
    "zero_pitch": "parameter",
    "sum_z": "parameter",
    "sum_phi": "parameter",
    "sum_zphi": "parameter",
    "sum_phisqr": "parameter",
    "hel_pitch": "output",
    "phid": "output",
    "dz": "output",
    "loss": "output",
}
LEAST_SQUARES_PITCH_VALIDITY_BOUNDS = {
    "zero_pitch": (0.0, None),
}

# Main branch; the runtime function adds a same-z rotation-sense fallback.
HELIX_DIRECTION_EXPR = sp.Eq(hel_dz, z2 - z1)
HELIX_DIRECTION_DIM_MAP = {
    **HELIX_CENTER_DIM_MAP,
    "hel_pitch": LENGTH,
    "x1": LENGTH,
    "y1": LENGTH,
    "z1": LENGTH,
    "x2": LENGTH,
    "y2": LENGTH,
    "z2": LENGTH,
    "hel_dz": LENGTH,
}
HELIX_DIRECTION_VARIABLES = {
    "hel_xm": "input",
    "hel_ym": "input",
    "hel_pitch": "input",
    "x1": "input",
    "y1": "input",
    "z1": "input",
    "x2": "input",
    "y2": "input",
    "z2": "input",
    "hel_dz": "output",
}

# Distance invariant once the Newton solve has produced the nearest point.
NEAREST_POINT_DISTANCE_EXPR = sp.Eq(
    dist**2,
    (x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2,
)
NEAREST_POINT_DISTANCE_DIM_MAP = {
    "x0": LENGTH,
    "y0": LENGTH,
    "z0": LENGTH,
    **HELIX_CENTER_DIM_MAP,
    "hel_r": LENGTH,
    "hel_pitch": LENGTH,
    "x": LENGTH,
    "y": LENGTH,
    "z": LENGTH,
    "x1": LENGTH,
    "y1": LENGTH,
    "z1": LENGTH,
    "dist": LENGTH,
    "iterations": COUNT,
}
NEAREST_POINT_DISTANCE_VARIABLES = {
    "x0": "input",
    "y0": "input",
    "z0": "input",
    "hel_xm": "input",
    "hel_ym": "input",
    "hel_r": "input",
    "hel_pitch": "input",
    "x": "input",
    "y": "input",
    "z": "input",
    "iterations": "parameter",
    "x1": "output",
    "y1": "output",
    "z1": "output",
    "dist": "output",
}
NEAREST_POINT_DISTANCE_VALIDITY_BOUNDS = {
    "hel_r": (0.0, None),
    "dist": (0.0, None),
    "iterations": (1.0, None),
}
