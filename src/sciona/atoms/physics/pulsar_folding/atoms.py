"""Auto-generated verified atom wrapper."""

import numpy as np
import icontract
from sciona.ghost.decorators import symbolic_atom

from .dimensions import BANDPASS_CORRECTION_DIM_MAP, DM_BRUTE_FORCE_DIM_MAP
from .expressions import (
    BANDPASS_CORRECTION_BIBLIOGRAPHY,
    BANDPASS_CORRECTION_EQUATION,
    BANDPASS_CORRECTION_VALIDITY_BOUNDS,
    BANDPASS_CORRECTION_VARIABLES,
    DM_BRUTE_FORCE_BIBLIOGRAPHY,
    DM_BRUTE_FORCE_CONSTANTS,
    DM_BRUTE_FORCE_EQUATION,
    DM_BRUTE_FORCE_VALIDITY_BOUNDS,
    DM_BRUTE_FORCE_VARIABLES,
)
from .witnesses import witness_dm_can_brute_force, witness_spline_bandpass_correction


@symbolic_atom(
    witness_dm_can_brute_force,
    expr=DM_BRUTE_FORCE_EQUATION,
    dim_map=DM_BRUTE_FORCE_DIM_MAP,
    validity_bounds=DM_BRUTE_FORCE_VALIDITY_BOUNDS,
    variables=DM_BRUTE_FORCE_VARIABLES,
    constants=DM_BRUTE_FORCE_CONSTANTS,
    bibliography=DM_BRUTE_FORCE_BIBLIOGRAPHY,
)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def dm_can_brute_force(data: np.ndarray) -> np.ndarray:
    """Performs a brute-force shift search to maximize the signal-to-noise ratio of a folded profile.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    # Brute-force DM search: try shifts and find SNR-maximizing one
    best_snr = -np.inf
    best_profile = data.copy()
    n = len(data)
    for shift in range(n):
        rolled = np.roll(data, -shift)
        snr = np.mean(rolled) / (np.std(rolled) + 1e-15)
        if snr > best_snr:
            best_snr = snr
            best_profile = rolled
    return best_profile

@symbolic_atom(
    witness_spline_bandpass_correction,
    expr=BANDPASS_CORRECTION_EQUATION,
    dim_map=BANDPASS_CORRECTION_DIM_MAP,
    validity_bounds=BANDPASS_CORRECTION_VALIDITY_BOUNDS,
    variables=BANDPASS_CORRECTION_VARIABLES,
    bibliography=BANDPASS_CORRECTION_BIBLIOGRAPHY,
)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def spline_bandpass_correction(data: np.ndarray) -> np.ndarray:
    """Subtracts instrument-induced artifacts across frequency channels using interpolative splines.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    # Spline bandpass correction: fit and subtract a smooth baseline
    from scipy.interpolate import UnivariateSpline
    x = np.arange(len(data), dtype=np.float64)
    spline = UnivariateSpline(x, data, s=len(data))
    return data - spline(x)
