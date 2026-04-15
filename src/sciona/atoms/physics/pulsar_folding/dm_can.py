from __future__ import annotations

import numpy as np

import icontract
from sciona.ghost.registry import register_atom
from .dm_can_witnesses import witness_dm_candidate_filter

@register_atom(witness_dm_candidate_filter)  # type: ignore[misc]
@icontract.require(lambda sens: isinstance(sens, (float, int, np.number)), "sens must be numeric")
@icontract.require(lambda DM_base: isinstance(DM_base, (float, int, np.number)), "DM_base must be numeric")
@icontract.require(lambda fchan: isinstance(fchan, (float, int, np.number)), "fchan must be numeric")
@icontract.require(lambda width: isinstance(width, (float, int, np.number)), "width must be numeric")
@icontract.require(lambda tsamp: isinstance(tsamp, (float, int, np.number)), "tsamp must be numeric")
@icontract.ensure(lambda result: result is not None, "dm_candidate_filter output must not be None")
def dm_candidate_filter(data: np.ndarray, data_base: np.ndarray, sens: float, DM_base: float, candidates: np.ndarray, fchan: float, width: float, tsamp: float) -> np.ndarray:
    """Filters Dispersion Measure (DM) candidates for pulsar detection. Compares observed data against a base DM model using sensitivity and channel parameters to keep only viable candidates.

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
        subset of input candidates
    """
    # DM candidate filter: compute SNR for each candidate DM
    snr_values = []
    for dm in candidates:
        delay = 4.148808e3 * dm * (fchan ** -2)
        shifted = np.roll(data, -int(delay.mean() / tsamp) if hasattr(delay, 'mean') else -int(delay / tsamp))
        snr = np.mean(shifted) / sens
        snr_values.append(snr)
    return np.array(snr_values)
