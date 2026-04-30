"""Symbolic scalar relations for Skyfield vector atoms."""

from __future__ import annotations

import sympy as sp

from .dimensions import ANGLE, ANGULAR_RATE, LENGTH, VELOCITY

(
    rx,
    ry,
    rz,
    vx,
    vy,
    vz,
    range_,
    latitude,
    longitude,
    range_rate,
    latitude_rate,
    longitude_rate,
    ux,
    uy,
    uz,
    wx,
    wy,
    wz,
    u_norm,
    w_norm,
    theta,
) = sp.symbols(
    "rx ry rz vx vy vz range latitude longitude range_rate "
    "latitude_rate longitude_rate ux uy uz wx wy wz u_norm w_norm theta"
)


SKYFIELD_BIBLIOGRAPHY = ["skyfield2019ascl", "repo_skyfield"]

SPHERICAL_RANGE_RATE_EXPR = sp.Eq(
    range_rate,
    (rx * vx + ry * vy + rz * vz) / range_,
)
SPHERICAL_RATES_DIM_MAP = {
    "r": LENGTH,
    "v": VELOCITY,
    "rx": LENGTH,
    "ry": LENGTH,
    "rz": LENGTH,
    "vx": VELOCITY,
    "vy": VELOCITY,
    "vz": VELOCITY,
    "range": LENGTH,
    "latitude": ANGLE,
    "longitude": ANGLE,
    "range_rate": VELOCITY,
    "latitude_rate": ANGULAR_RATE,
    "longitude_rate": ANGULAR_RATE,
}
SPHERICAL_RATES_VARIABLES = {
    "r": "input",
    "v": "input",
    "rx": "input",
    "ry": "input",
    "rz": "input",
    "vx": "input",
    "vy": "input",
    "vz": "input",
    "range": "output",
    "latitude": "output",
    "longitude": "output",
    "range_rate": "output",
    "latitude_rate": "output",
    "longitude_rate": "output",
}
SPHERICAL_RATES_VALIDITY_BOUNDS = {
    "range": (0.0, None),
}

VECTOR_ANGLE_EXPR = sp.Eq(
    sp.cos(theta),
    (ux * wx + uy * wy + uz * wz) / (u_norm * w_norm),
)
VECTOR_ANGLE_DIM_MAP = {
    "u": LENGTH,
    "v": LENGTH,
    "ux": LENGTH,
    "uy": LENGTH,
    "uz": LENGTH,
    "wx": LENGTH,
    "wy": LENGTH,
    "wz": LENGTH,
    "u_norm": LENGTH,
    "w_norm": LENGTH,
    "theta": ANGLE,
}
VECTOR_ANGLE_VARIABLES = {
    "u": "input",
    "v": "input",
    "ux": "input",
    "uy": "input",
    "uz": "input",
    "wx": "input",
    "wy": "input",
    "wz": "input",
    "u_norm": "parameter",
    "w_norm": "parameter",
    "theta": "output",
}
VECTOR_ANGLE_VALIDITY_BOUNDS = {
    "theta": (0.0, float(sp.pi)),
    "u_norm": (0.0, None),
    "w_norm": (0.0, None),
}

