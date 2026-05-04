"""Symbolic relations for pulsar pipeline atoms."""

from __future__ import annotations

import sympy as sp


(
    delay,
    K,
    DM,
    freq_emitted,
    shift_samples,
    tsamp,
    fchan,
    width,
    time_index,
    channel_index,
    input_sample,
    output_sample,
    profile_phase,
    folded_sum,
    multiples,
    n_chans,
    period,
    snr,
    peak,
    avg_noise,
) = sp.symbols(
    "delay K DM freq_emitted shift_samples tsamp fchan width time_index "
    "channel_index input_sample output_sample profile_phase folded_sum "
    "multiples n_chans period snr peak avg_noise"
)


PULSAR_PIPELINE_BIBLIOGRAPHY = ["lorimer2005pulsar", "repo_pulsar_pipeline"]

DISPERSION_DELAY_CONSTANT = 1.0 / 0.000241
DELAY_FROM_DM_EXPR = sp.Eq(delay, K * DM * freq_emitted**-2)
DELAY_FROM_DM_CONSTANTS = {"K": DISPERSION_DELAY_CONSTANT}
DELAY_FROM_DM_VARIABLES = {
    "delay": "output",
    "K": "constant",
    "DM": "input",
    "freq_emitted": "input",
}
DELAY_FROM_DM_VALIDITY_BOUNDS = {
    "DM": (0.0, None),
    "freq_emitted": (0.0, None),
}

DEDISPERSE_SHIFT_EXPR = sp.Eq(shift_samples, delay / tsamp)
DEDISPERSE_VARIABLES = {
    "shift_samples": "output",
    "delay": "input",
    "tsamp": "parameter",
    "DM": "input",
    "fchan": "input",
    "width": "parameter",
    "time_index": "input",
    "channel_index": "input",
    "input_sample": "input",
    "output_sample": "output",
}
DEDISPERSE_VALIDITY_BOUNDS = {
    "DM": (0.0, None),
    "fchan": (0.0, None),
    "width": (0.0, None),
    "tsamp": (0.0, None),
}

FOLD_SIGNAL_EXPR = sp.Eq(profile_phase, folded_sum / (multiples * n_chans))
FOLD_SIGNAL_VARIABLES = {
    "profile_phase": "output",
    "folded_sum": "input",
    "multiples": "parameter",
    "n_chans": "parameter",
    "period": "parameter",
}
FOLD_SIGNAL_VALIDITY_BOUNDS = {
    "multiples": (1.0, None),
    "n_chans": (1.0, None),
    "period": (1.0, None),
}

SNR_EXPR = sp.Eq(snr, sp.log(peak / avg_noise))
SNR_VARIABLES = {
    "snr": "output",
    "peak": "input",
    "avg_noise": "input",
}
SNR_VALIDITY_BOUNDS = {
    "peak": (0.0, None),
    "avg_noise": (0.0, None),
}
