from __future__ import annotations

from sciona.ghost.dimensions import DIMENSIONLESS, FREQUENCY, METER, SECOND


# Dispersion measure is a column electron density: electron count per area.
# The conventional pc cm^-3 unit is handled by the numerical constant.
DISPERSION_MEASURE = METER.power(-2)

# K is stored in the conventional numerical units used by the implementation:
# delay_ms = K * DM_pc_cm^-3 * f_MHz^-2. Dimensionally it carries the
# conversion factors needed to map column density and frequency to delay.
DISPERSION_DELAY_CONSTANT_DIMENSION = METER.power(2).multiply(SECOND).multiply(
    FREQUENCY.power(2)
)

DISPERSION_DELAY_DIM_MAP = {
    "delay": SECOND,
    "K": DISPERSION_DELAY_CONSTANT_DIMENSION,
    "DM": DISPERSION_MEASURE,
    "DM_base": DISPERSION_MEASURE,
    "candidates": DISPERSION_MEASURE,
    "fchan": FREQUENCY,
    "sens": DIMENSIONLESS,
    "width": SECOND,
    "tsamp": SECOND,
}

DM_BRUTE_FORCE_DIM_MAP = {
    "snr": DIMENSIONLESS,
    "shifted_mean": DIMENSIONLESS,
    "shifted_std": DIMENSIONLESS,
    "epsilon": DIMENSIONLESS,
    "data": DIMENSIONLESS,
    "best_profile": DIMENSIONLESS,
    "shift": DIMENSIONLESS,
}

BANDPASS_CORRECTION_DIM_MAP = {
    "corrected_sample": DIMENSIONLESS,
    "raw_sample": DIMENSIONLESS,
    "baseline_sample": DIMENSIONLESS,
    "data": DIMENSIONLESS,
    "sample_index": DIMENSIONLESS,
}
