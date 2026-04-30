from __future__ import annotations

import numpy as np

import icontract
from sciona.ghost.decorators import symbolic_atom
from .dimensions import DISPERSION_DELAY_DIM_MAP
from .dm_can_witnesses import witness_dm_candidate_filter
from .expressions import (
    DISPERSION_DELAY_BIBLIOGRAPHY,
    DISPERSION_DELAY_CONSTANT,
    DISPERSION_DELAY_CONSTANTS,
    DISPERSION_DELAY_EQUATION,
    DISPERSION_DELAY_VALIDITY_BOUNDS,
    DISPERSION_DELAY_VARIABLES,
)


@symbolic_atom(  # type: ignore[misc]
    witness_dm_candidate_filter,
    expr=DISPERSION_DELAY_EQUATION,
    dim_map=DISPERSION_DELAY_DIM_MAP,
    validity_bounds=DISPERSION_DELAY_VALIDITY_BOUNDS,
    constants=DISPERSION_DELAY_CONSTANTS,
    bibliography=DISPERSION_DELAY_BIBLIOGRAPHY,
    variables=DISPERSION_DELAY_VARIABLES,
)
@icontract.require(lambda sens: isinstance(sens, (float, int, np.number)), "sens must be numeric")
@icontract.require(lambda DM_base: isinstance(DM_base, (float, int, np.number)), "DM_base must be numeric")
@icontract.require(lambda fchan: isinstance(fchan, (float, int, np.number)), "fchan must be numeric")
@icontract.require(lambda width: isinstance(width, (float, int, np.number)), "width must be numeric")
@icontract.require(lambda tsamp: isinstance(tsamp, (float, int, np.number)), "tsamp must be numeric")
@icontract.ensure(lambda result: result is not None, "dm_candidate_filter output must not be None")
def dm_candidate_filter(data: np.ndarray, data_base: np.ndarray, sens: float, DM_base: float, candidates: np.ndarray, fchan: float, width: float, tsamp: float) -> np.ndarray:
    """Scores Dispersion Measure (DM) candidates for pulsar detection.

    Compares observed data against a base DM model using sensitivity and
    channel parameters to produce one score per candidate.

    Args:
        data: Input data.
        data_base: Input data.
        sens: sens > 0
        DM_base: DM_base >= 0
        candidates: Input data.
        fchan: fchan > 0
        width: width > 0
        tsamp: tsamp > 0

    Returns:
        One floating-point score per candidate.
    """
    # DM candidate filter: compute SNR for each candidate DM
    snr_values = []
    for dm in candidates:
        delay = DISPERSION_DELAY_CONSTANT * dm * (fchan ** -2)
        shifted = np.roll(data, -int(delay.mean() / tsamp) if hasattr(delay, 'mean') else -int(delay / tsamp))
        snr = np.mean(shifted) / sens
        snr_values.append(snr)
    return np.array(snr_values)
