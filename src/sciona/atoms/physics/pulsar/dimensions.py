"""Dimension signatures for pulsar pipeline symbolic atoms."""

from __future__ import annotations

from sciona.ghost.dimensions import DIMENSIONLESS, FREQUENCY, METER, SECOND


DISPERSION_MEASURE = METER.power(-2)

DISPERSION_DELAY_CONSTANT_DIMENSION = METER.power(2).multiply(SECOND).multiply(
    FREQUENCY.power(2)
)

PULSAR_DELAY_DIM_MAP = {
    "delay": SECOND,
    "K": DISPERSION_DELAY_CONSTANT_DIMENSION,
    "DM": DISPERSION_MEASURE,
    "freq_emitted": FREQUENCY,
}

PULSAR_DEDISPERSION_DIM_MAP = {
    "shift_samples": DIMENSIONLESS,
    "delay": SECOND,
    "tsamp": SECOND,
    "DM": DISPERSION_MEASURE,
    "fchan": FREQUENCY,
    "width": FREQUENCY,
    "time_index": DIMENSIONLESS,
    "channel_index": DIMENSIONLESS,
    "input_sample": DIMENSIONLESS,
    "output_sample": DIMENSIONLESS,
}

PULSAR_FOLD_DIM_MAP = {
    "profile_phase": DIMENSIONLESS,
    "folded_sum": DIMENSIONLESS,
    "multiples": DIMENSIONLESS,
    "n_chans": DIMENSIONLESS,
    "period": DIMENSIONLESS,
}

PULSAR_SNR_DIM_MAP = {
    "snr": DIMENSIONLESS,
    "peak": DIMENSIONLESS,
    "avg_noise": DIMENSIONLESS,
}
