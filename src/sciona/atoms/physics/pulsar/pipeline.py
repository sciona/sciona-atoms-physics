"""Pulsar Folding atoms implementing Dispersion Measure (DM)-trial dedispersion and signal folding."""

from __future__ import annotations

import math

import icontract
import numpy as np

from sciona.ghost.decorators import symbolic_atom
from .dimensions import (
    PULSAR_DEDISPERSION_DIM_MAP,
    PULSAR_DELAY_DIM_MAP,
    PULSAR_FOLD_DIM_MAP,
    PULSAR_SNR_DIM_MAP,
)
from .expressions import (
    DEDISPERSE_SHIFT_EXPR,
    DEDISPERSE_VALIDITY_BOUNDS,
    DEDISPERSE_VARIABLES,
    DELAY_FROM_DM_CONSTANTS,
    DELAY_FROM_DM_EXPR,
    DELAY_FROM_DM_VALIDITY_BOUNDS,
    DELAY_FROM_DM_VARIABLES,
    FOLD_SIGNAL_EXPR,
    FOLD_SIGNAL_VALIDITY_BOUNDS,
    FOLD_SIGNAL_VARIABLES,
    PULSAR_PIPELINE_BIBLIOGRAPHY,
    SNR_EXPR,
    SNR_VALIDITY_BOUNDS,
    SNR_VARIABLES,
)
from .witnesses import (
    witness_dedisperse,
    witness_delay_from_dm,
    witness_fold_signal,
    witness_snr,
)


@symbolic_atom(
    witness_delay_from_dm,
    expr=DELAY_FROM_DM_EXPR,
    dim_map=PULSAR_DELAY_DIM_MAP,
    validity_bounds=DELAY_FROM_DM_VALIDITY_BOUNDS,
    variables=DELAY_FROM_DM_VARIABLES,
    constants=DELAY_FROM_DM_CONSTANTS,
    bibliography=PULSAR_PIPELINE_BIBLIOGRAPHY,
)
@icontract.require(lambda DM: DM >= 0, "DM must be non-negative")
@icontract.require(lambda freq_emitted: freq_emitted >= 0, "Frequency must be non-negative")
@icontract.ensure(lambda result: result >= 0, "Delay must be non-negative")
def delay_from_DM(DM: float, freq_emitted: float) -> float:
    """Compute frequency-dependent propagation delay from a medium's Dispersion Measure (DM).

    Args:
        DM: Dispersion measure value (non-negative).
        freq_emitted: Emission frequency (non-negative).

    Returns:
        Non-negative propagation delay in seconds.
    """
    if freq_emitted > 0.0:
        return DM / (0.000241 * freq_emitted * freq_emitted)
    return 0.0


@symbolic_atom(
    witness_dedisperse,
    expr=DEDISPERSE_SHIFT_EXPR,
    dim_map=PULSAR_DEDISPERSION_DIM_MAP,
    validity_bounds=DEDISPERSE_VALIDITY_BOUNDS,
    variables=DEDISPERSE_VARIABLES,
    bibliography=PULSAR_PIPELINE_BIBLIOGRAPHY,
)
@icontract.require(lambda data: data.ndim == 2, "Input data must be 2D (Time, Frequency)")
@icontract.require(lambda tsamp: tsamp > 0, "tsamp must be positive")
@icontract.require(lambda width: width > 0, "Channel width must be positive")
@icontract.ensure(lambda result, data: result.shape == data.shape, "Output must preserve input shape")
def de_disperse(
    data: np.ndarray,
    DM: float,
    fchan: float,
    width: float,
    tsamp: float,
) -> np.ndarray:
    """Apply frequency-dependent delay correction to align a 2D spectrogram across channels.

    Args:
        data: 2D input array of shape (time, frequency).
        DM: Dispersion Measure value.
        fchan: Frequency of the first channel.
        width: Channel bandwidth.
        tsamp: Sampling interval in seconds (must be positive).

    Returns:
        De-dispersed 2D array with the same shape as input.
    """
    clean = np.array(data, copy=True)
    n_time, n_chans = clean.shape

    for chan in range(n_chans):
        freq_emitted = chan * width + fchan
        time_delay = int(delay_from_DM(DM, freq_emitted) / tsamp)

        if 0 < time_delay < n_time:
            shifted = clean[: n_time - time_delay, chan]
            clean[time_delay:n_time, chan] = shifted
            clean[:time_delay, chan] = 0.0
        elif time_delay >= n_time:
            clean[:, chan] = 0.0

    return clean


@symbolic_atom(
    witness_fold_signal,
    expr=FOLD_SIGNAL_EXPR,
    dim_map=PULSAR_FOLD_DIM_MAP,
    validity_bounds=FOLD_SIGNAL_VALIDITY_BOUNDS,
    variables=FOLD_SIGNAL_VARIABLES,
    bibliography=PULSAR_PIPELINE_BIBLIOGRAPHY,
)
@icontract.require(lambda data: data.ndim == 2, "Input data must be 2D")
@icontract.require(lambda period: period > 0, "Folding period must be positive")
@icontract.ensure(lambda result, period: result.shape == (period,), "Profile length must match period")
def fold_signal(data: np.ndarray, period: int) -> np.ndarray:
    """Fold a 1D signal at a known period to build a phase-averaged periodic profile.

    Args:
        data: 2D input array of shape (time, frequency).
        period: Folding period in samples (must be positive).

    Returns:
        1D array of length period containing the phase-averaged profile.
    """
    n_time = data.shape[0]
    n_chans = data.shape[1]
    multiples = n_time // period

    if multiples < 1:
        return np.zeros(period, dtype=np.float64)

    folded = np.zeros((period, n_chans), dtype=np.float64)
    for i in range(multiples):
        folded += data[i * period : (i + 1) * period, :]

    folded /= float(multiples)
    return folded.mean(axis=1)


@symbolic_atom(
    witness_snr,
    expr=SNR_EXPR,
    dim_map=PULSAR_SNR_DIM_MAP,
    validity_bounds=SNR_VALIDITY_BOUNDS,
    variables=SNR_VARIABLES,
    bibliography=PULSAR_PIPELINE_BIBLIOGRAPHY,
)
@icontract.require(lambda arr: arr.ndim == 1, "Input must be 1D")
@icontract.require(lambda arr: len(arr) > 0, "Input array must not be empty")
@icontract.ensure(lambda result: result >= 0, "SNR must be non-negative")
def SNR(arr: np.ndarray) -> float:
    """Compute Signal-to-Noise Ratio (SNR) of a periodic profile.

    Args:
        arr: 1D input array representing the periodic profile.

    Returns:
        Non-negative SNR value (log of peak-to-mean ratio).
    """
    if np.all(arr == 0):
        return 0.0

    peak = float(arr[int(np.argmax(arr))])
    avg_noise = float(abs(np.mean(arr)))
    if avg_noise <= 0:
        return 0.0

    ratio = peak / avg_noise
    if ratio <= 0:
        return 0.0

    return float(math.log(ratio))
