from __future__ import annotations

import sympy as sp


(
    K,
    DM,
    fchan,
    delay,
    snr,
    shifted_mean,
    shifted_std,
    epsilon,
    data,
    best_profile,
    shift,
    corrected_sample,
    raw_sample,
    baseline_sample,
    sample_index,
) = sp.symbols(
    "K DM fchan delay snr shifted_mean shifted_std epsilon data best_profile "
    "shift corrected_sample raw_sample baseline_sample sample_index"
)

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

DM_BRUTE_FORCE_EQUATION = sp.Eq(snr, shifted_mean / (shifted_std + epsilon))
DM_BRUTE_FORCE_CONSTANTS = {
    "epsilon": 1e-15,
}
DM_BRUTE_FORCE_VARIABLES = {
    "snr": "output",
    "shifted_mean": "input",
    "shifted_std": "input",
    "epsilon": "constant",
    "data": "input",
    "best_profile": "output",
    "shift": "parameter",
}
DM_BRUTE_FORCE_VALIDITY_BOUNDS = {
    "shifted_std": (0.0, None),
    "epsilon": (0.0, None),
    "shift": (0.0, None),
}
DM_BRUTE_FORCE_BIBLIOGRAPHY = [
    "lorimer2005pulsar",
    "repo_pulsar_folding",
]

BANDPASS_CORRECTION_EQUATION = sp.Eq(
    corrected_sample,
    raw_sample - baseline_sample,
)
BANDPASS_CORRECTION_VARIABLES = {
    "corrected_sample": "output",
    "raw_sample": "input",
    "baseline_sample": "parameter",
    "data": "input",
    "sample_index": "input",
}
BANDPASS_CORRECTION_VALIDITY_BOUNDS = {
    "sample_index": (0.0, None),
}
BANDPASS_CORRECTION_BIBLIOGRAPHY = [
    "repo_pulsar_folding",
]
