from __future__ import annotations

import sympy as sp


K, DM, fchan, delay = sp.symbols("K DM fchan delay")

DISPERSION_DELAY_CONSTANT = 4.148808e3
DISPERSION_DELAY_EQUATION = sp.Eq(delay, K * DM * fchan**-2)

DISPERSION_DELAY_CONSTANTS = {
    "K": DISPERSION_DELAY_CONSTANT,
}

DISPERSION_DELAY_VARIABLES = {
    "delay": "output",
    "K": "constant",
    "DM": "input",
    "DM_base": "input",
    "candidates": "input",
    "fchan": "input",
    "sens": "parameter",
    "width": "parameter",
    "tsamp": "parameter",
}

DISPERSION_DELAY_VALIDITY_BOUNDS = {
    "DM": (0.0, None),
    "DM_base": (0.0, None),
    "candidates": (0.0, None),
    "fchan": (0.0, None),
    "sens": (0.0, None),
    "width": (0.0, None),
    "tsamp": (0.0, None),
}

DISPERSION_DELAY_BIBLIOGRAPHY = [
    "lorimer2005pulsar",
    "repo_pulsar_folding",
]
